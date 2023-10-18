from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

import schemas

import database

from fastapi import Depends, FastAPI, HTTPException, status

SECRET_KEY = "274ae11418dc7fa5770a6cfc1ac07b1cfe13cad08b91de0f01aaf65d6a88f814"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    if username in db:
        user_data = db[username]
        #return UserInDB(**user_data)
        return schemas.AuthenticatedUser(**user_data)
    

# def userInDB(db, username:str):
#     if username in db:
#         user_data = db[username]
#         return schemas.UserInDB(**user_data)
def userInDB(db, email:str):
    if email in db:
        user_data = db[email]
        return schemas.UserInDB(**user_data)
    

    
def authenticate_user(username: str, password: str):
    user = get_user(database.db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    
    #access_token_expires = timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    # access_token_expires = timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    user.access_token = create_access_token(data={"sub": user.username})
    
    return user

def create_access_token(data: dict):

    expires_delta = timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

# def create_access_token(data: dict, expires_delta: timedelta or None = None):

#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow + timedelta(minutes=15)

#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

#     return encoded_jwt

async def get_current_user(token: str = Depends(oauth_2_scheme)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception
        
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credential_exception
    
    user = get_user(database.db, username=token_data.username)
    if user is None:
        raise credential_exception
    
    return user

async def get_current_active_user(current_user: schemas.UserInDB = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return current_user