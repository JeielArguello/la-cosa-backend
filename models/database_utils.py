from fastapi import HTTPException, Body
from models.database import Partida
from pony.orm import db_session
from pony.orm import *
from .database import *


def get_db() -> Database:
    return db


@db_session
def get_exist_user_in_game(id_user: int):
    with db_session:
        partidas_con_id_creador = Partida.get(id_jugador_creador=id_user)

    return partidas_con_id_creador != None


@db_session
def get_exist_user(id_user: int):
    with db_session:
        jugador_en_db = Jugador.get(id=id_user)

    return jugador_en_db != None


@db_session
def get_match(db: Database, match_id: int):
    match_ = db.Partida.get(id=match_id)
    return match_


db_session


def get_exist_match(id_match: int):
    with db_session:
        match_in_db = Partida.get(id=id_match)

    return match_in_db != None


@db_session
def database_utils_iniciar_partida(match_id: int, user_id: int):
    with db_session:
        try:
            partida = Partida.get(id=match_id)
        except:
            raise HTTPException(
                status_code=400, detail="Error al acceder a la base de datos.")

        if partida is None:
            raise HTTPException(
                status_code=400, detail="El match_id no es válido")

        if partida.id_jugador_creador != user_id:
            raise HTTPException(
                status_code=400, detail="El user_id no corresponde al creador de la ")

        if partida.iniciado == True:
            raise HTTPException(
                status_code=400, detail="La partida ya esta inicializada.")

        try:
            partida.iniciado = True
        except:
            raise HTTPException(
                status_code=400, detail="No se le pudo inicializar la ")
