import random
from fastapi import HTTPException
from models.crud import get_name_carta
from models.game import Juego
from utils.action_utils import *


def play_lanzallamas(atacante_in: int, objetivo_in: int, juego: Juego):
    # get indices
    len_posiciones = len(juego.posiciones)
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
    for jugador in juego.jugadores_en_partida:
        if jugador.id == objetivo_in:
            # objetivo = jugador
            jugador.set_muerto()
    # juego.jugadores_en_partida.remove(objetivo)
    del juego.posiciones[indice_objetivo]
    del juego.posiciones[indice_objetivo]


def play_hacha(atacante_in: int, objetivo_in: int, juego: Juego):
    # get indices
    len_posiciones = len(juego.posiciones)
    indice_objetivo = juego.posiciones.index(objetivo_in)
    indice_atacante = juego.posiciones.index(atacante_in)
    indice_posicion_intermedia = get_posicion_intermedia(
        len_posiciones, indice_objetivo, indice_atacante)
    validar_posiciones_vecinas(
        indice_atacante,
        indice_objetivo,
        len_posiciones)
    validar_puerta(indice_posicion_intermedia, juego)
    juego.posiciones[indice_posicion_intermedia] = 0


def play_sospecha(atacante_in: int, objetivo_in: int, juego: Juego):
    jugador_objetivo = get_jugador(objetivo_in, juego)
    jugador_atacante = get_jugador(atacante_in, juego)
    carta_id = random.choice(jugador_objetivo.cartas)
    nombre_carta = get_name_carta(carta_id)
    if carta_id not in jugador_objetivo.cartas:
        raise HTTPException(
            status_code=400,
            detail="No se pudo obtener una carta del jugador objetivo")
    msg = {"mensaje":jugador_atacante.name+" jugo carta "+nombre_carta +" contra "+jugador_objetivo.name,
           "cartaMostrar": carta_id}
    return msg

def play_vigila_tus_espaldas(juego: Juego):
    juego.sentido = juego.sentido * (-1)


def play_mas_vale_que_corras(atacante_in: int, objetivo_in: int, juego: Juego):
    # validar si esta en cuarentena
    validar_cuarentena(objetivo_in, juego)
    # obtengo el indice de los jugadores
    indice_objetivo = juego.posiciones.index(objetivo_in)
    indice_atacante = juego.posiciones.index(atacante_in)
    # hago el intercambio de posiciones
    juego.posiciones[indice_objetivo] = atacante_in
    juego.posiciones[indice_atacante] = objetivo_in
