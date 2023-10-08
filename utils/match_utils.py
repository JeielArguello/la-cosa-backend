from models.crud import *
from models.database_utils import *
from models.lobby_models import all_lobby

@db_session
def listar_partidas():
    list_rooms = []
        
    partidas = get_matches()

    for partida in partidas:
        cant_jugadores = db_cantidad_jugadores(partida.id)
        if cant_jugadores is None:
            raise HTTPException(status_code=400,detail="No se pudo obtener la partida")

        if not partida.iniciado  and cant_jugadores<partida.maximo_jugadores :
            list_rooms.append({'id_partida': partida.id,
                                'name_partida': partida.nombre,
                                'cantidad_jugadores': cant_jugadores,
                                'cantidad_jugadores_maximos': partida.maximo_jugadores,
                                'contrasena': (partida.contrasena is not None),
                                'iniciado':partida.iniciado})

    return list_rooms

def get_lobby(lobby_id : int):
    for p in all_lobby:
        if p.id_partida == lobby_id:
            lobby = p
    return lobby
