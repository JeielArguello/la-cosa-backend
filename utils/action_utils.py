
from fastapi import HTTPException

from models.game import Juego


def validar_posiciones_vecinas(
        indice_objetivo: int,
        indice_atacante: int,
        len_posiciones: int):
    primero = min(indice_objetivo, indice_atacante)
    segundo = max(indice_objetivo, indice_atacante)
    if (primero + 2 != segundo) and (primero !=
                                     0 or segundo != len_posiciones - 2):
        raise HTTPException(
            status_code=400,
            detail="Los jugadores no son vecinos")


def get_posicion_intermedia(len_posiciones, indice_jugador1, indice_jugador2):
    border_one = (indice_jugador1 == 0 and indice_jugador2 ==
                  len_posiciones - 1)
    border_two = (indice_jugador2 == 0 and indice_jugador1 ==
                  len_posiciones - 1)
    if (border_one or border_two):
        posicion = len_posiciones - 1
    else:
        posicion = min(indice_jugador1, indice_jugador2) + 1
    return posicion


def validar_obstaculo(indice_posicion_intermedia: int, juego: Juego):
    if juego.posiciones[indice_posicion_intermedia] != 0:
        raise HTTPException(
            status_code=400,
            detail="Hay un Obstaculo entre los jugadores")

def validar_jugadores_en_juego(atacante_in: int, objetivo_in: int, juego: Juego):
    if atacante_in not in juego.posiciones:
        raise HTTPException(
            status_code=400, detail="Atacante no esta en el juego")
    if objetivo_in not in juego.posiciones:
        raise HTTPException(
            status_code=400, detail="Objetivo no esta en el juego")

def validar_cuarentena(objetivo_in: int, juego: Juego):
    pass
