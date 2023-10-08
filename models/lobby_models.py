
from typing import List, Optional
from fastapi import WebSocket
from pydantic import BaseModel

from models.crud import get_estado_partida


class CreateLobbyRequest(BaseModel):
    id_usuario_creador: int
    id_name: str
    contraseña: Optional[str] = None
    num_max_jugadores: int
    num_min_jugadores: int


class Lobby:
    def __init__(self, id_usuario_creador: int,
                       id_name: str ,
                       contraseña: str,
                       num_max_jugadores: int,
                       num_min_jugadores: int,
                       id_partida : int 
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

    def add_player(self,user_id):
        self.cantidad_jugadores = self.cantidad_jugadores + 1
        self.users_id.append(user_id)

    async def broadcast_lobby(self, message: dict):
        for p in self.ws_players:
            await p.send_json(message)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.ws_players.append(websocket)
        await self.broadcast_lobby({"message": "se agrego un usuario al lobby"})
        await self.broadcast_lobby(get_estado_partida(self.id_partida))
        
    async def disconnect(self, websocket: WebSocket):
        self.ws_players.remove(websocket)
        await websocket.send_text("cerrando conexion")
        await websocket.close(reason="cliente pide desconexion")
        await self.broadcast_lobby("se desconecto un usuario")

        


all_lobby: List[Lobby] = []
