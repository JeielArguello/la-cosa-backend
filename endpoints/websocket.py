from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from utils.match_utils import *
from typing import List

router = APIRouter()

#websocket general para listar partidas
@router.websocket('/match/list')
async def websocket_endpoint_list(websocket: WebSocket):
    
     try:
          #acepto el websocket del cliente
          await websocket.accept()
          #agrego el ws a la lista de ws
          ws_players_list.append(websocket)
          await broadcast({"message":"Usuario viendo lista de partida"})
          #le envio el mensaje para que el cliente pida la lista de partias actualizadas
          await websocket.send_text("A")
          
          while True:
               #espero hasta recibir un mensaje
               msg = await websocket.receive()
               #verifico que no sea una mala desconexion 
               websocket._raise_on_disconnect(msg)
               #verifico si el cliente se quiere desconectar
               if(msg["text"] == "desconexion"): 
                    ws_players_list.remove(websocket)
                    await websocket.send_json("cerrando conexion")
                    await websocket.close(reason="cliente pide desconexion")
                    break
               
     except WebSocketDisconnect:
          if websocket in ws_players_list:
               ws_players_list.remove(websocket)

async def broadcast( message: dict):
        for p in ws_players_list:
            await p.send_json(message)

      

ws_players_list: List[WebSocket] = []

