from endpoints.user import router as user_router
from endpoints.user import *
from fastapi.middleware.cors import CORSMiddleware
from endpoints.match import router as matchRouter
from pony.orm import db_session
from models.database import create_db
from functools import partial
from fastapi import FastAPI, Body, HTTPException
from fastapi.routing import APIRouter
from models.card_init import create_cards
#from models.crud import create_10Partidas

app = FastAPI()

origins = [
    "http://localhost:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(user_router, prefix="/user")
app.include_router(matchRouter)


@app.on_event("startup")
def startup_db():
    create_db()
    create_cards()


@app.get("/")
async def root():
    return {"message": "Hello there!"}
