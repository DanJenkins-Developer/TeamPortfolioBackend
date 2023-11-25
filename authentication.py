import os
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from datetime import datetime, timedelta
from jose import JWTError, jwt
import schemas
from crud import get_user_by_email
from sqlalchemy.orm import Session
from fastapi import Depends
from db_utils import get_db
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

load_dotenv()

# DATABASE_URL = os.getenv("SECRET_KEY")

# SECRET_KEY = os.getenv("SECRET_KEY")
# ALGORITHM = os.getenv("ALGORITHM")
# ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

SECRET_KEY = "274ae11418dc7fa5770a6cfc1ac07b1cfe13cad08b91de0f01aaf65d6a88f814"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)

# def get_user(db, email: str):
#     if email in db:
#         user_data = db[email]
#         return schemas.UserInDB(**user_data)
    # return schemas.AuthenticatedUser(**user_data)


def authenticate_user(email: str, password: str, db: Session = Depends(get_db)):
    # user = get_user(db, email)
    user = get_user_by_email(db, email)
    if not user:
        # return False
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect email or password", headers={"WWW-Authenticate": "Bearer"})
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect email or password", headers={"WWW-Authenticate": "Bearer"})
        # return False

    access_token = create_access_token(data={"sub": user.email})

    return schemas.UserInDB(first_name=user.first_name, last_name=user.last_name, phone_number=user.phone_number, profile_picture_id=user.profile_picture_link, email=user.email, access_token=access_token)
    # return schemas.AuthenticatedUser(email=user.email,
    #                                  access_token=access_token)

    # return user


def create_access_token(data: dict):

    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt
