import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from models.lobby_models import all_lobby
from utils.match_utils import *
from typing import List

router = APIRouter()

#websocket para sala
@router.websocket('/lobby/{match_id}')
async def websocket_endpoint(websocket: WebSocket, match_id: int):
     
     lobby = get_lobby(match_id)

     await lobby.connect(websocket)

     try:
          while True:
               msg = await websocket.receive()
               await websocket._raise_on_disconnect(msg)
               await lobby.broadcast_lobby(msg)

     except WebSocketDisconnect:
          if websocket in lobby.ws_players:
               await lobby.disconnect(websocket)


async def broadcast( message: dict):
        for p in ws_players_list:
            await p.send_json(message)

      

ws_players_list: List[WebSocket] = []

#websocket general para listar partidas
@router.websocket('/match/list')
async def websocket_endpoint(websocket: WebSocket):
    
     try:
          await websocket.accept()
          ws_players_list.append(websocket)
          await broadcast({"message":"Usuario viendo lista de partida"})
          await websocket.send_json(listar_partidas())
          
          while True:
               msg = await websocket.receive() 
               if(msg["text"] == "desconeccion"): 
                    ws_players_list.remove(websocket)
                    print(len(ws_players_list))
               await broadcast(listar_partidas())
               await broadcast(msg)
     except :
          if websocket in ws_players_list:
               ws_players_list.remove(websocket)
          print(f"error")
     
