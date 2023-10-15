from fastapi import Depends, FastAPI, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext

from fastapi.middleware.cors import CORSMiddleware

from middleware import authentication

from Database import database

from Schemas import schemas

from typing import Annotated

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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
    photo: Annotated[UploadFile, File()],
    email: Annotated[str, Form()]
):
    return {
        "file_size": photo.content_type,
        "email": email
        #print("Hello")
    }


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # print("Testing ::" + form_data.username)
    # print("Testing ::" + form_data.password)
    user = authentication.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    
    return {"access_token": user.access_token, "token_type": "bearer"}

@app.post("/login", response_model=schemas.Token)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):

    user = authentication.userInDB(database.db, form_data.username)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})

    if not authentication.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})

    access_token = authentication.create_access_token(data={"sub": user.username})

    #return {"User": user.username, "access_token": access_token, "token_type":"bearer"}
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(authentication.get_current_active_user)):
    return current_user

@app.get("/users/items")
async def read_own_items(current_user: schemas.User = Depends(authentication.get_current_active_user)):
    return [{"item_id": 1, "owner":current_user}]




# pwd = get_password_hash("dan1234")
# print(pwd)
# Dependency
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


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


# @app.get("/users/{user_id}", response_model=schemas.User)
# def read_user(user_id: int, db: Session = Depends(get_db)):
#     db_user = crud.get_user(db, user_id=user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user

