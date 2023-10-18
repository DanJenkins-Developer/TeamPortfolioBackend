from pydantic import BaseModel
from fastapi import File
from typing import Optional

class EmailPasswordRequestForm(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str or None = None

# class User(BaseModel):
#     username: str
#     email: str or None = None
#     full_name: str or None = None
#     disabled: bool or None = None

class User(BaseModel):
    email: str 

class CreateUser(User):
    first_name: str
    last_name: str
    phone_number: str
    profile_picture_id: str or None = None
    password: str


class AuthenticatedUser(User):
    #hashed_password: str
    access_token: str or None = None

class UserInDB(User):
    first_name: str
    last_name: str
    phone_number: str
    profile_picture_id: str or None = None

    class Config:
        from_attributes = True