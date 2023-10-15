from fastapi import HTTPException
from models.game import Juego


def play_lanzallamas(atacante_in: int, objetivo_in: int, juego: Juego):
    # get indices
    len_posiciones = len(juego.posiciones)
    if atacante_in not in juego.posiciones:
        raise HTTPException(
            status_code=400, detail="Atacante no esta en el juego")
    if objetivo_in not in juego.posiciones:
        raise HTTPException(
            status_code=400, detail="Objetivo no esta en el juego")
    indice_objetivo = juego.posiciones.index(objetivo_in)
    indice_atacante = juego.posiciones.index(atacante_in)
    indice_posicion_intermedia = get_posicion_intermedia(
        len_posiciones, indice_objetivo, indice_atacante)
    # check vecinos
    validar_posiciones_vecinas(
        indice_atacante,
        indice_objetivo,
        len_posiciones)
    # check obstaculos
    validar_obstaculo(indice_posicion_intermedia, juego)
    # check defensa
    # if defensa:
    #     pass
    # get Jugador objetivo
    for jugador in juego.jugadores_en_partida:
        if jugador.id == objetivo_in:
            objetivo = jugador
    # eliminar jugador y posiciones
    juego.jugadores_en_partida.remove(objetivo)
    del juego.posiciones[indice_objetivo]
    del juego.posiciones[indice_objetivo]


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
