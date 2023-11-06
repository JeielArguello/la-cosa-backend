# from fastapi import HTTPException
from models.game import Juego
from utils.action_utils import *
from models.crud import get_name


def play_tres_cuatro(player_orig: int, juego: Juego, card_id: int):
    for index in range(0, len(juego.posiciones)):
        if juego.posiciones[index] == "p":
            juego.posiciones[index] = 0
    jugador = get_jugador(player_orig, juego)
    msg = {
        "mensaje": jugador.name +
        " jugó la carta Tres,Cuatro..."}
    juego.agregar_log(msg["mensaje"])
    juego.agregar_log(
        jugador.name + " elimino todas las puertas atrancadas.")
    return msg


def play_ups(atacante_in: int, juego: Juego, card_id: int):
    jugador = get_jugador(atacante_in, juego)
    if jugador:
        cartas = jugador.get_cartas()
        msg = {
            "mensaje": jugador.name + " jugó la carta Ups.",
            "cartaMostrar": cartas
        }
        juego.agregar_log(msg["mensaje"])
        juego.agregar_log(
            jugador.name + " mostró su mano de cartas.")
        return (msg)
    else:
        return {"error": "no se pudieron mostrar cartas."}
