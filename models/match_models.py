
from typing import List, Optional
from fastapi import WebSocket
from pydantic import BaseModel

class CreateMatchRequest(BaseModel):
    id_usuario_creador: int
    id_name : str
    contraseña : Optional[str] = None
    num_max_jugadores : int
    num_min_jugadores : int

class JoinMatchRequest(BaseModel):
    match_id: int
    id_player: int

class Match:
    id_Match: int 
    
    def __init__(self,match:CreateMatchRequest) -> None:
        self.name=match.id_name
        self.ws_players : List[WebSocket] = []
        self.owner = match.id_usuario_creador
        self.player_amount: int = 1
        self.is_start: bool = False


    def add_player(self):
        self.player_amount = self.player_amount + 1
        

    async def broadcast(self, message: dict):
        for p in self.ws_players:
            await p.send_json(message)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.ws_players.append(websocket)
        await self.broadcast({"message":"se agrego un usuario"})

    async def disconnect(self, websocket: WebSocket):
        await self.broadcast({"message":"se desconecto un usuario"})
        self.ws_players.remove(websocket)

all_matchs : List[Match] = []
