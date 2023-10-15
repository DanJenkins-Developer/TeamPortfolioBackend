from sqlalchemy.orm import Session

#from . import models, schemas
#import models, schemas
import models

from Schemas import schemas

from middleware import authentication

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.CreateUser):

    print(user)
    # Set up variables to pass to the model
    #fake_hashed_password = user.password + "notreallyhashed"
    hashed_password = authentication.get_password_hash(user.password)

    print("\n\n\n")
    print("USER PASSWORD :: ")
    print(hashed_password)
    print("\n\n\n")
    #create user model
    #db_user = models.User(email=user.email, hashed_password=fake_hashed_password, picture_path = user.picture_path)
    db_user = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        phone_number=user.phone_number,
        email=user.email,
        hashed_password = hashed_password
    )
    # add to DB
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user