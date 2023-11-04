# from fastapi import HTTPException
from models.game import Juego
from utils.action_utils import *


def play_ups(atacante_in: int, juego: Juego, card_id: int):
    jugador = get_jugador(atacante_in, juego)
    if jugador:
        cartas = jugador.get_cartas()
        msg = {
            "mensaje": jugador.name + " jugó carta Ups.",
            "cartaMostrar": cartas
        }
        return (msg)
    else:
        return {"error": "no se pudieron mostrar cartas."}
