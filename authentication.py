from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
from db_utils import get_db
from fastapi import Depends
from sqlalchemy.orm import Session
from crud import get_user_by_email
import schemas
from jose import JWTError, jwt
from datetime import datetime, timedelta

from dotenv import load_dotenv
import os
load_dotenv()

#DATABASE_URL = os.getenv("SECRET_KEY")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")



def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, email: str):
    if email in db:
        user_data = db[email]
        return schemas.UserInDB(**user_data)
        #return schemas.AuthenticatedUser(**user_data)
    
def authenticate_user(email: str, password: str, db: Session = Depends(get_db)):
    #user = get_user(db, email)
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    
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