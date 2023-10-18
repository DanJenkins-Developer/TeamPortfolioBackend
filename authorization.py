from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, FastAPI, HTTPException, status

from db_utils import get_db

from sqlalchemy.orm import Session

from jose import JWTError, jwt

import schemas

from crud import get_user_by_email

SECRET_KEY = "274ae11418dc7fa5770a6cfc1ac07b1cfe13cad08b91de0f01aaf65d6a88f814"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30



bearer_scheme = HTTPBearer()

def get_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    return credentials.credentials

def authorize(token: str = Depends(get_token), db: Session = Depends(get_db)):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credential_exception
        
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credential_exception
    
    user = get_user_by_email(db, token_data.email)
    if user is None:
        raise credential_exception
    
    print(user)
    return user

    
    


