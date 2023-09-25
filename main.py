from fastapi import FastAPI
from models.database import create_db
from models.card_init import create_cards
from endpoints.user import *
from endpoints.user import router as user_router

app = FastAPI()


@app.on_event("startup")
def startup_db():
    create_db()
    create_cards()


@app.get("/")
async def root():
    return {"message": "Hello there!"}

app.include_router(user_router, prefix = "/user")