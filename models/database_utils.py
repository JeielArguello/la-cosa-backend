from pony.orm import *
from .database import * 


def get_db() -> Database:
    return db

@db_session
def get_exist_user(db:Database,id_user : int):
    with db_session:
        partidas_con_id_creador = db.Partida.get(id_jugador_creador=id_user)
        Partida.select().show()

    return partidas_con_id_creador!=None

@db_session
def get_match(db:Database,match_id:int):
    match_ = db.Partida.get(id = match_id) 
    return match_