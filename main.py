from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

from fastapi.middleware.cors import CORSMiddleware

from middleware import authentication

SECRET_KEY = "274ae11418dc7fa5770a6cfc1ac07b1cfe13cad08b91de0f01aaf65d6a88f814"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


#Testing
#from . import crud, models, schemas
# import crud, models, schemas
# from database import SessionLocal, engine

# models.Base.metadata.create_all(bind=engine)


db = {
    "tim": {
        "username": "tim",
        "full_name": "Tim Ruscica",
        "email": "time@gmail.com",
        "hashed_password": "$2b$12$9g6sxsPCIEhMlUpnzn0fhOvsdlUO7qaMOz5HZqCG53zSMSDWYJO1S",
        "disabled": False
    }
}

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

class AuthenticatedUser(User):
    hashed_password: str
    access_token: str or None = None

class UserInDB(User):
    hashed_password: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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

# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)

# def get_password_hash(password):
#     return pwd_context.hash(password)

def get_user(db, username: str):
    if username in db:
        user_data = db[username]
        #return UserInDB(**user_data)
        return AuthenticatedUser(**user_data)
    
def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not authentication.verify_password(password, user.hashed_password):
        return False
    
    access_token_expires = timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    user.access_token = authentication.create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    
    return user

# def create_access_token(data: dict, expires_delta: timedelta or None = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow + timedelta(minutes=15)

#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

#     return encoded_jwt

async def get_current_user(token: str = Depends(oauth_2_scheme)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception
        
        token_data = TokenData(username=username)
    except JWTError:
        raise credential_exception
    
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credential_exception
    
    return user

async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return current_user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    print("Testing ::" + form_data.username)
    print("Testing ::" + form_data.password)
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})

    # access_token_expires = timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    # access_token = authentication.create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    
    return {"access_token": user.access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.get("/users/items")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
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

