from datetime import date
from pydantic import BaseModel

class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    picture_path: str

    class Config:
        orm_mode = True
