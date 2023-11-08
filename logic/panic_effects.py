# from fastapi import HTTPException
from models.game import Juego
from utils.action_utils import *
from models.crud import get_name


def play_cuerdas_podridas(player_orig: int, juego: Juego):
    for jugador in juego.jugadores_en_partida:
        if jugador.get_cuartena():
            jugador.remove_cuartena()
    jugador = get_jugador(player_orig, juego)
    msg = {
        "mensaje": jugador.name +
        " jugó la carta Cuerdas Podridas."}
    juego.agregar_log(msg["mensaje"])
    juego.agregar_log(
        jugador.name + " eliminó todas las cuarentenas del juego.")
    return msg


def play_tres_cuatro(player_orig: int, juego: Juego):
    for index in range(0, len(juego.posiciones)):
        if juego.posiciones[index] == "p":
            juego.posiciones[index] = 0
    jugador = get_jugador(player_orig, juego)
    msg = {
        "mensaje": jugador.name +
        " jugó la carta Tres,Cuatro..."}
    juego.agregar_log(msg["mensaje"])
    juego.agregar_log(
        jugador.name + " eliminó todas las puertas atrancadas.")
    return msg


def play_ups(atacante_in: int, juego: Juego):
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
