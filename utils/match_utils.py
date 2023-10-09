from models.crud import *
from models.database_utils import *
from models.lobby_models import all_lobby

def get_lobby(lobby_id : int):
    for p in all_lobby:
        if p.id_partida == lobby_id:
            lobby = p
    return lobby
