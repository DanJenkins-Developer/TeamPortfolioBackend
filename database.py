from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# db = {
#     "tim": {
#         "username": "tim",
#         "full_name": "Tim Ruscica",
#         "email": "time@gmail.com",
#         "hashed_password": "$2b$12$9g6sxsPCIEhMlUpnzn0fhOvsdlUO7qaMOz5HZqCG53zSMSDWYJO1S",
#         "disabled": False
#     }
# }