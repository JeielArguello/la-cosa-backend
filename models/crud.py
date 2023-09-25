from pony.orm import *
from .database import * 
from .match_models import CreateMatchRequest



"""
MATCH
"""

@db_session
def init_match(match_:CreateMatchRequest):
    with db_session:
        new_match = Partida(nombre = match_.id_name,
                            iniciado = False,
                            id_jugador_creador= match_.id_usuario_creador,
                            minimo_jugadores = match_.num_min_jugadores,
                            maximo_jugadores = match_.num_max_jugadores,
                            contrasena = match_.contraseña,
                            jugadores = [])
        Partida.select().show()
        """ for p in Ju
        new_match.jugadores.add(player) """
    return new_match.id

@db_session
def get_exist_user(id_user : int):
    with db_session:
        partidas_con_id_creador = Partida.get(id_jugador_creador=id_user)
        Partida.select().show()

    return partidas_con_id_creador!=None

@db_session
def get_match(match_id:int):
    match_ = Partida.get(id = match_id) 
    return match_