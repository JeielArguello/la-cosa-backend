from fastapi import FastAPI
from database import *
from init_db import initialize_database

app = FastAPI()


@app.on_event("startup")
def startup_db():
    initialize_database()


@app.get("/")
async def root():
    return {"message": "Hello World"}
