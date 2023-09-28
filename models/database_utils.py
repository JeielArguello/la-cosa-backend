from fastapi import HTTPException, status
from pony.orm import *
from .database import *


def get_db() -> Database:
    return db

# USUARIO


@db_session
def get_exist_user(id_user: int):
    jugador_en_db = Jugador.get(id=id_user)
    return jugador_en_db is not None

# PARTIDA


def validar_partida(
        id_usuario_creador: int,
        num_max_jugadores: int,
        num_min_jugadores: int):
    if not get_exist_user(id_usuario_creador):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario no existe"
        )
    if get_exist_user_in_game(id_usuario_creador):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario ya ingresado en una partida"
        )
    if num_min_jugadores < 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Numero minimo de jugadores menor a 4"
        )
    if num_max_jugadores > 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Numero maximo de jugadores mayor a 11"
        )


@db_session
def get_exist_user_in_game(id_user: int):
    partidas_con_id_creador = Partida.get(id_jugador_creador=id_user)
    return partidas_con_id_creador is not None


@db_session
def get_match(db: Database, match_id: int):
    match_ = db.Partida.get(id=match_id)
    return match_


@db_session
def get_exist_match(id_match: int):
    match_in_db = Partida.get(id=id_match)
    return match_in_db is not None


@db_session
def database_utils_iniciar_partida(match_id: int, user_id: int):
    try:
        partida = Partida.get(id=match_id)
    except BaseException:
        raise HTTPException(
            status_code=400, detail="Error al acceder a la base de datos.")

    if partida is None:
        raise HTTPException(
            status_code=400, detail="El match_id no es válido")

    if partida.id_jugador_creador != user_id:
        raise HTTPException(
            status_code=400,
            detail="El user_id no corresponde al creador de la ")

    if partida.iniciado:
        raise HTTPException(
            status_code=400, detail="La partida ya esta inicializada.")

    try:
        partida.iniciado = True
    except BaseException:
        raise HTTPException(
            status_code=400, detail="No se le pudo inicializar la ")
