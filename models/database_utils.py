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
        raise ValueError("usuario no existe.")
    if get_exist_user_in_game(id_usuario_creador):
        raise ValueError("Usuario ya ingresado en una partida.")
    if num_min_jugadores < 4:
        raise ValueError("Numero minimo de jugadores menor a 4.")
    if num_max_jugadores > 12:
        raise ValueError("Numero maximo de jugadores mayor a 11.")


@db_session
def validar_entrada_partida(id_player: int, id_match: int):
    # existe el usuario
    if not get_exist_user(id_player):
        raise ValueError("Usuario no existe")
    # usuario en otra partida
    if get_exist_user_in_game(id_player):
        raise ValueError("Usuario ya ingresado en una partida")
    # existe partida
    if not get_exist_match(id_match):
        raise ValueError("Partida no existe")
    partida = get_match(id_match)
    if partida is None:
        raise HTTPException(
            detail="no se pudo cargar la partida de base de datos")
    if not get_partida_habilitada(partida):
        raise ValueError("Partida no habilitada")
    if partida.iniciado:
        raise ValueError("Partida ya iniciada")


@db_session
def get_partida_habilitada(partida_select: Partida):
    cantidad_jugadores = partida_select.jugadores.count()
    cantidad_max = partida_select.maximo_jugadores
    return cantidad_max > cantidad_jugadores


@db_session
def get_exist_user_in_game(id_user: int):
    jugador = get(p for p in Jugador if p.id == id_user)
    check = jugador.partida is not None
    return check


@db_session
def get_match(match_id: int):
    match = get(p for p in Partida if p.id == match_id)
    return match


@db_session
def get_exist_match(id_match: int):
    match_in_db = Partida.get(id=id_match)
    return match_in_db is not None


@db_session
def database_utils_iniciar_partida(match_id: int, user_id: int):

    partida = Partida.get(id=match_id)

    if partida is None:
        raise HTTPException(status_code=400, detail="El match_id no es válido")

    if partida.id_jugador_creador != user_id:
        raise HTTPException(
            status_code=400,
            detail="El user_id no corresponde al creador de la partida")

    if partida.iniciado:
        raise HTTPException(
            status_code=400, detail="La partida ya esta inicializada.")

    partida.iniciado = True

    if not partida.iniciado:
        raise HTTPException(
            status_code=400, detail="No se puede inicializar la partida. ")
