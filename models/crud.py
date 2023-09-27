from pony.orm import *
from .database import * 
from .database_utils import *
from models.database import*
from typing import Dict


"""
    MATCH
"""

#Create
@db_session
def init_match(match_):
    with db_session:

        # Crear la nueva partida con el conjunto de jugadores
        new_match = Partida(
            nombre=match_["id_name"],
            iniciado=False,
            id_jugador_creador=match_["id_usuario_creador"],
            minimo_jugadores=match_["num_min_jugadores"],
            maximo_jugadores=match_["num_max_jugadores"],
            contrasena=match_["contraseña"],
            jugadores=[]
        )
        if get_exist_user(match_["id_usuario_creador"]):
            user_creator = Jugador.get(id=match_["id_usuario_creador"])
            if user_creator is not None:
                new_match.jugadores.add(user_creator)
                Jugador.select().show()
    return new_match.id

@db_session
def update_add_player(user_id:int,match_id:int):
    if get_exist_user(user_id):
        user_creator = Jugador.get(id=user_id)
        match_update = Partida.get(id=match_id)        
        if user_creator is not None and match_update is not None :
            match_update.jugadores.add(user_creator)
            


"""
    USER
"""
#Create
@db_session
def db_create_user(db: Database, nombre: str) -> Dict[str, int]:
    user_in_db = db.Jugador(nombre = nombre)
    user_in_db.flush()
    result = {"user_name": user_in_db.nombre, "id": user_in_db.id}
    return result
