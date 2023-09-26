from sqlalchemy.schema import Column
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.types import String, Integer, Text
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True)
    picture_path = Column(String)
    hashed_password = Column(String)

