from models.crud import *
from models.database_utils import *
from models.lobby_models import all_lobby


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
        raise ValueError("Numero maximo de jugadores mayor a 12.")
    if num_max_jugadores < num_min_jugadores:
        raise ValueError(
            "Numero maximo de jugadores debe ser mayor al numero minimo.")


def get_lobby(lobby_id: int):
    for p in all_lobby:
        if p.id_partida == lobby_id:
            lobby = p
    return lobby
