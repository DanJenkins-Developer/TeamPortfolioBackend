# uvicorn main:app --reload
# python3 -m http.server 8080

from s3_bucket import s3_client
from fastapi import Depends, FastAPI, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from db_utils import get_db
from sqlalchemy.orm import Session
from authorization import authorize
from typing import Annotated
import crud
import models
import schemas
import middleware
import authentication

from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

from s3_bucket_utils import put_profile_picture

app = FastAPI()


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/register")
async def register(
    first_name: Annotated[str, Form()],
    last_name: Annotated[str, Form()],
    phone_number: Annotated[str, Form()],
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    photo: Annotated[UploadFile, File()],
    db: Session = Depends(get_db)
):
    # check if user exists
    db_user = crud.get_user_by_email(db, email=email)

    # if so throw an error
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        # Upload profile picture to s3 bucket
        photo_url = await put_profile_picture(photo)
    except NoCredentialsError:
        raise HTTPException(
            status_code=500, detail="Credentials not available for AWS S3")
    except PartialCredentialsError:
        raise HTTPException(
            status_code=500, detail="Incomplete credentials for AWS S3")
    except ClientError as e:
        raise HTTPException(
            status_code=500, detail=f"AWS S3 Client Error: {e}")

        # Save photo_url instead of photo_name
    profile_picture_url = photo_url
    # Construct user schema to pass to crud function
    user = schemas.CreateUser(
        email=email,
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        profile_picture_id=profile_picture_url,
        password=password
    )

    # Create user
    db_user = crud.create_user(db=db, user=user)

    access_token = middleware.create_access_token(data={"sub": db_user.email})

    # Return same info that I would with users.me
    return {"access_token": access_token,
            "token_type": "bearer",
            "profile_picture_link": profile_picture_url}


# @app.post("/login", response_model=schemas.Token)
# async def login_user(form_data: schemas.EmailPasswordRequestForm = Depends(), db: Session = Depends(get_db) ):

#     #user = middleware.userInDB(database.db, form_data.username)

#     db_user = crud.get_user_by_email(db, email=form_data.email)

#     if not db_user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password", headers={"WWW-Authenticate": "Bearer"})

#     if not middleware.verify_password(form_data.password, db_user.hashed_password):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password", headers={"WWW-Authenticate": "Bearer"})

#     access_token = middleware.create_access_token(data={"sub": db_user.email})

#     #return {"User": user.username, "access_token": access_token, "token_type":"bearer"}
#     return {"access_token": access_token, "token_type": "bearer"}

# @app.post("/login", response_model=schemas.AuthenticatedUser)
@app.post("/login")
async def login_user(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):

    # user = middleware.userInDB(database.db, form_data.username)
    # email = form_data.email
    # password = form_data.password

    auth_db_user = authentication.authenticate_user(email, password, db)

    # access_token = middleware.create_access_token(data={"sub": db_user.email})

    # return {"User": user.username, "access_token": access_token, "token_type":"bearer"}
    # return {"access_token": access_token, "token_type": "bearer"}
    access_token = middleware.create_access_token(
        data={"sub": auth_db_user.email})

    # test
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=schemas.UserInDB)
async def read_users_me(current_user: models.User = Depends(authorize)):
    return current_user

# @app.get("/users/items")
# async def read_own_items(current_user: schemas.User = Depends(middleware.get_current_active_user)):
#     return [{"item_id": 1, "owner":current_user}]

# @app.post("/users/", response_model=schemas.User)
# def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     db_user = crud.get_user_by_email(db, email=user.email)
#     if db_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
#     return crud.create_user(db=db, user=user)


# @app.get("/users/", response_model=list[schemas.User])
# def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     users = crud.get_users(db, skip=skip, limit=limit)
#     return users
