from pydantic import BaseModel


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str
    picture_path: str


class User(UserBase):
    id: int
    #picture_list: str

    class Config:
        from_attributes = True
