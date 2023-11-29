# uvicorn main:app --reload
# python3 -m http.server 8080

# from s3_bucket import s3_client
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
from pydantic import EmailStr, ValidationError
import stripe
from starlette.responses import RedirectResponse
import uvicorn

from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

from s3_bucket_utils import put_profile_picture


from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# SET STRIPE API KEY
stripe.api_key = os.getenv("STRIPE_TEST_SECRET_KEY")
YOUR_DOMAIN = os.getenv("FRONTEND_URL")

app = FastAPI()


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "https://team-portfolio-480.onrender.com"
]

app.add_middleware(
    # CORS Middleware to allow requests from localhost:8080
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/register")
async def register(
    # Get form data from request
    first_name: Annotated[str, Form()],
    last_name: Annotated[str, Form()],
    phone_number: Annotated[str, Form()],
    # email: Annotated[str, Form()],
    email: Annotated[EmailStr, Form()],
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
            "profile_picture_link": profile_picture_url,
            "first_name": db_user.first_name,
            "last_name": db_user.last_name,
            "phone_number": db_user.phone_number,
            "email": db_user.email}

    # Probably should add some timestamp here for checking
    # freshness of data on frontend


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
    # return {"access_token": access_token, "token_type": "bearer"}

    # Return same info that I would with users.me
    return {"access_token": access_token,
            "token_type": "bearer",
            "profile_picture_link": auth_db_user.profile_picture_id,
            "first_name": auth_db_user.first_name,
            "last_name": auth_db_user.last_name,
            "phone_number": auth_db_user.phone_number}


@app.get("/users/me", response_model=schemas.UserInDB)
async def read_users_me(current_user: models.User = Depends(authorize)):
    return current_user


@app.post("/process-payment")
async def process_payment(amount: int, currency: str, token: str):
    try:
        # Create a charge using the Stripe API
        charge = stripe.Charge.create(
            amount=amount,
            currency=currency,
            # Stripe token obtained from the client-side (e.g., Stripe.js)
            source=token,
            description="Payment for FastAPI Store",  # Add a description for the payment
        )

        # You can handle the charge object as per your requirements
        # For example, log the payment or perform other actions

        # Return a success response
        return {"status": "success", "charge_id": charge.id}

    except stripe.error.CardError as e:
        # Handle specific Stripe errors
        return {"status": "error", "message": str(e)}
    except stripe.error.StripeError as e:
        # Handle generic Stripe errors
        return {"status": "error", "message": "Something went wrong. Please try again later."}


@app.post('/connection-token')
async def connection_token():
    try:
        connection_token = stripe.terminal.ConnectionToken.create()
        # If you want to return only the secret part
        return {"secret": connection_token.secret}
    except Exception as e:
        # Handle exceptions (e.g., from Stripe API) and return a suitable error response
        raise HTTPException(status_code=400, detail=str(e))


@app.post('/create-checkout-session')
async def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': 'price_1OHWwrBJJOeDqi7auCOahOfp',
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=YOUR_DOMAIN + '/success.html',
            cancel_url=YOUR_DOMAIN + '/cancel.html',
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

     # Redirect the client to the checkout session URL
    return RedirectResponse(url=checkout_session.url, status_code=303)


if __name__ == "__main__":
    # Retrieve the port number from the environment variable set by Render
    # or default to 8000 if it's not set.
    port = int(os.environ.get('PORT', 8000))
    # Start Uvicorn with `host` set to '0.0.0.0' to bind to all interfaces
    # and `port` set to the retrieved port.
    uvicorn.run(app, host="0.0.0.0", port=port)

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
