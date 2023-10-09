import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from utils.match_utils import *
from typing import List
from logic.game import Juego
from endpoints.game import get_global_juego


router = APIRouter()

#websocket para sala
@router.websocket('/lobby/{match_id}')
async def websocket_endpoint_lobby(websocket: WebSocket, match_id: int):
     
     #obtengo el lobby al que se quiere conectar
     lobby = get_lobby(match_id)

     #conecto el ws del cliente a el lobby y aviso a todos que se unio alguien
     # actualizando la cantidad de jugadores
     await lobby.connect(websocket)

     try:
          while True:
               #espero un mensaje
               msg = await websocket.receive() 

               #verifico que no sea una mala desconexion 
               websocket._raise_on_disconnect(msg)

               #verifico si el cliente se quiere desconectar
               if(msg["text"] == "desconexion"): 
                    await lobby.disconnect(websocket)
                    break
               #
               await lobby.broadcast_lobby(msg)

     except WebSocketDisconnect:
          if websocket in lobby.ws_players:
               lobby.ws_players.remove(websocket)
          await lobby.broadcast_lobby("se desconecto un usuario")

#websocket para juego
@router.websocket('/game/{match_id}')
async def websocket_endpoint_game(websocket: WebSocket, match_id: int):
     
     game = get_global_juego(match_id)

     await game.connect_game(websocket)

     try:
          while True:
               msg = await websocket.receive() 
               websocket._raise_on_disconnect(msg)
               if(msg["text"] == "desconexion"): 
                    await game.disconnect_game(websocket)
                    break
               await game.broadcast_global(msg)

     except WebSocketDisconnect:
          if websocket in game.ws_players:
               game.ws_players.remove(websocket)
          await game.broadcast_global("se desconecto un usuario")
     
