from dotenv import load_dotenv
import os

load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv('DATABASE_URL')

#DATABASE_URL = "mysql+mysqlconnector://root:13881qwe@teamportfoliodb.clujlsnvyjra.us-east-2.rds.amazonaws.com:3306/team_portfolio"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

