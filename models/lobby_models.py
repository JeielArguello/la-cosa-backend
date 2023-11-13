
from typing import List, Optional
from fastapi import WebSocket
from fastapi import HTTPException
from utils.game_utils import global_juegos
from models.game import Juego
from models.constants import *


class Lobby:
    def __init__(self, id_usuario_creador: int,
                 id_name: str,
                 contraseña: Optional[str],
                 num_max_jugadores: int,
                 num_min_jugadores: int,
                 id_partida: int
                 ) -> None:
        self.id_usuario_creador = id_usuario_creador
        self.id_name = id_name
        self.contrasena: contraseña
        self.num_max_jugadores: num_max_jugadores
        self.num_min_jugadores: num_min_jugadores
        self.id_partida = id_partida
        self.cantidad_jugadores: int = 1
        self.iniciada: bool = False
        self.ws_players: List[WebSocket] = []
        self.users_id: List[int] = [id_usuario_creador]

    def add_player(self, user_id):
        self.cantidad_jugadores = self.cantidad_jugadores + 1
        self.users_id.append(user_id)

    def remove_player(self, user_id):
        self.cantidad_jugadores = self.cantidad_jugadores - 1
        self.users_id.remove(user_id)

    def list_players(self):
        list_player = self.users_id
        return list_player

    async def init_game(self):
        juego = Juego(
            self.id_partida,
            self.cantidad_jugadores,
            self.id_usuario_creador,
            self.users_id)
        juego.repartir_cartas(self.cantidad_jugadores)
        global_juegos.append(juego)
        self.iniciada = True

    async def broadcast_lobby(self, message: dict):
        for p in self.ws_players:
            await p.send_json(message)
            await p.send_json("reset")

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.ws_players.append(websocket)
        await self.broadcast_lobby(CAMBIO_ESTADO_LOBBY)

    async def disconnect(self, websocket: WebSocket):
        self.ws_players.remove(websocket)
        await websocket.send_json("cerrando conexion")
        await websocket.close(reason="cliente pide desconexion")
        await self.broadcast_lobby(CAMBIO_ESTADO_LOBBY)


def delete_lobby(match_id):
    result = None
    for lobby in all_lobby:
        if lobby.id_partida == match_id:
            result = lobby
    if(result is None):
        raise HTTPException(
            status_code=400, detail="No se encontro el lobby")
    all_lobby.remove(result)


all_lobby: List[Lobby] = []
