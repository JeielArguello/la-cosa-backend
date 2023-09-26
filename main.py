from fastapi import FastAPI, status
from models.database import create_db
from models.card_init import create_cards
from pony.orm import db_session, select
from models.database import Carta
from fastapi.middleware.cors import CORSMiddleware
from endpoints.user import *
from endpoints.user import router as user_router

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


@app.on_event("startup")
def startup_db():
    create_db()
    create_cards()


@app.get("/")
async def root():
    return {"message": "Hello there!"}


@db_session
def construir_mazo(num_jugadores: int):
    cartas_seleccionadas = select(
        c.id for c in Carta if c.numero_jugadores <= num_jugadores)  # [:]
    # [{"nombre": c.nombre, "numero_jugadores": c.numero_jugadores, "tipo_dorso": c.tipo_dorso,
    mazo = list(cartas_seleccionadas)
    # "tipo_de_accion": c.tipo_de_accion, "descripcion": c.descripcion} for c in cartas_seleccionadas]
    return mazo


@app.get("/cards/deck", status_code=status.HTTP_200_OK)
async def deck_create(players_num: int):
    retorno = construir_mazo(players_num)
    return retorno

# game.py llamar desde ahi la construir mazo
