from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}