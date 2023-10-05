
from typing import List, Optional
from fastapi import WebSocket
from pydantic import BaseModel


class CreateMatchRequest(BaseModel):
    id_usuario_creador: int
    id_name: str
    contraseña: Optional[str] = None
    num_max_jugadores: int
    num_min_jugadores: int


class Match:
    id_Match: int
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

    def add_player(self):
        self.player_amount = self.player_amount + 1

    async def broadcast(self, message: dict):
        for p in self.ws_players:
            await p.send_json(message)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.ws_players.append(websocket)
        await self.broadcast({"message": "se agrego un usuario"})

    async def disconnect(self, websocket: WebSocket):
        await self.broadcast({"message": "se desconecto un usuario"})
        self.ws_players.remove(websocket)


all_matchs: List[Match] = []
