from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


import database


class User(database.Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    phone_number = Column(String(255))
    email = Column(String(255), unique=True, index=True)
    profile_picture_link = Column(String(255), unique=True)
    hashed_password = Column(String(255))
    # picture_path = Column(String(255))
