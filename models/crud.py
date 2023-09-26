from pony.orm import *
from .database import * 
from .database_utils import *
from models.database import*
from typing import Dict


"""
MATCH
"""

@db_session
def init_match(db: Database, match_):
    with db_session:
        # Crear un conjunto vacío de Jugadores
       

        # Crear la nueva partida con el conjunto de jugadores
        new_match = db.Partida(
            nombre=match_["id_name"],
            iniciado=False,
            id_jugador_creador=match_["id_usuario_creador"],
            minimo_jugadores=match_["num_min_jugadores"],
            maximo_jugadores=match_["num_max_jugadores"],
            contrasena=match_["contraseña"],
            jugadores=[]  # Asignar el conjunto de jugadores
        )

        Partida.select().show()
        
        if get_exist_user(match_["id_usuario_creador"]):
            user_creator = Jugador.get(id=match_["id_usuario_creador"])
            if user_creator is not None:
                new_match.jugadores.add(user_creator)
                db.Jugador.select().show()
    return new_match.id



def get_db() -> Database:
    return db

@db_session
def db_create_user(db: Database, nombre: str) -> Dict[str, int]:
    user_in_db = db.Jugador(nombre = nombre)
    user_in_db.flush()
    result = {"user_name": user_in_db.nombre, "id": user_in_db.id}
    return result
