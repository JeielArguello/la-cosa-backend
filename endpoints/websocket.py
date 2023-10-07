from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from models.match_models import all_matchs
#from endpoints.match import iniciar_partida 
from utils.match_utils import *
from typing import List

router = APIRouter()

#websocket para sala
@router.websocket('/{match_id}')
async def websocket_endpoint(websocket: WebSocket, match_id: int):
    for p in all_matchs:
        if p.id_partida == match_id:
             match = p
    await match.connect(websocket)

    try:
         while True:
             msg = await websocket.receive()
             print(msg)
             if msg["text"] == "iniciar":
                #await iniciar_partida(1,1)
                await match.broadcast("se inicio la partida")
             await match.broadcast(msg)
    except WebSocketDisconnect:
         match.disconnect(websocket)
         await match.broadcast("Client left the chat")

    await match.disconnect(websocket)


async def broadcast( message: dict):
        for p in ws_players_list:
            await p.send_json(message)

async def disconnect(self, websocket: WebSocket):
        await self.broadcast({"message": "se desconecto un usuario"})
        self.ws_players.remove(websocket)

ws_players_list: List[WebSocket] = []

#websocket general para listar partidas
@router.websocket('/match/list')
async def websocket_endpoint(websocket: WebSocket):
    
     await websocket.accept()
     ws_players_list.append(websocket)
     await broadcast({"message":"Usuario viendo lista de partida"})
     while True:
          msg = await websocket.receive()
          await broadcast(msg)
          if msg["text"] == "iniciar":
                #await database_utils_iniciar_partida(1,1)
                await broadcast("se inicio la partida")
          await broadcast(listar_partidas())
          if(msg["text"] == "desconeccion"): 
               await disconnect(websocket)
   