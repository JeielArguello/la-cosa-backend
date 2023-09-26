from functools import partial
from fastapi import FastAPI, Body, HTTPException
from fastapi.routing import APIRouter
from models.card_init import create_cards
from models.database import create_db
#from models.crud import create_10Partidas
from pony.orm import db_session
from endpoints.match import router as matchRouter

app = FastAPI()

app.include_router(matchRouter)

@app.on_event("startup")
def startup_db():
    create_db()
    create_cards()

@app.get("/")
async def root():
    return {"message": "Hello there!"}
