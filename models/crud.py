from pony.orm import *
from .database import * 
from .match_models import CreateMatchRequest



"""
MATCH
"""

@db_session
def init_match(db:Database,match_:CreateMatchRequest):
    with db_session:
        new_match = db.Partida(nombre = match_.id_name,
                            iniciado = False,
                            id_jugador_creador= match_.id_usuario_creador,
                            minimo_jugadores = match_.num_min_jugadores,
                            maximo_jugadores = match_.num_max_jugadores,
                            contrasena = match_.contraseña,
                            jugadores = [])
        db.Partida.select().show()
        """ for p in Ju
        new_match.jugadores.add(player) """
    return new_match.id

from models.database import*
from typing import Dict


def get_db() -> Database:
    return db

@db_session
def db_create_user(db: Database, nombre: str) -> Dict[str, int]:
    user_in_db = db.Jugador(nombre = nombre)
    user_in_db.flush()
    result = {"user_name": user_in_db.nombre, "id": user_in_db.id}
    return result
