from pydantic import BaseModel
from fastapi import File
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str or None = None

class User(BaseModel):
    username: str
    email: str or None = None
    full_name: str or None = None
    disabled: bool or None = None

class NewUser(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    photo_name: str or None = None
    email: str 
    password: str
    disabled: bool or None = None


class AuthenticatedUser(User):
    hashed_password: str
    access_token: str or None = None

class UserInDB(User):
    hashed_password: str