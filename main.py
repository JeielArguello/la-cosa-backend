from fastapi import FastAPI, status
from models.database import create_db
from models.card_init import create_cards
from pony.orm import db_session, select
from models.database import Carta
app = FastAPI()


@app.on_event("startup")
def startup_db():
    create_db()
    create_cards()


@app.get("/")
async def root():
    return {"message": "Hello there!"}

@db_session
def construir_mazo(num_jugadores: int):
    cartas_seleccionadas = select(c for c in Carta if c.numero_jugadores > num_jugadores)[:]
    mazo = [{"nombre": c.nombre, "numero_jugadores": c.numero_jugadores, "tipo_dorso": c.tipo_dorso,
             "tipo_de_accion": c.tipo_de_accion, "descripcion": c.descripcion} for c in cartas_seleccionadas]
    return mazo

@app.get("/cards/deck", status_code = status.HTTP_200_OK)
async def deck_create(players_num: int): 
    if (players_num < 4 or players_num > 12): 
        return{"error": "Numero de jugadores incorrecto."} 
    retorno = construir_mazo(players_num)
    return retorno