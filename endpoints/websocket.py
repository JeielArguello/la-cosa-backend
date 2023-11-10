from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from utils.game_utils import get_global_juego
from utils.match_utils import *
from typing import List
import json
from models.constants import *


router = APIRouter()

# websocket general para listar partidas


@router.websocket('/match/list')
async def websocket_endpoint_list(websocket: WebSocket):
    try:
        # acepto el websocket del cliente
        await websocket.accept()
        # agrego el ws a la lista de ws
        ws_players_list.append(websocket)
        await broadcast({"message": "Usuario viendo lista de partida"})
        # le envio el mensaje para que el cliente pida la lista de partias
        # actualizadas
        await broadcast(CAMBIO_LISTAR_PARTIDA)
        while True:
            # espero hasta recibir un mensaje
            msg = await websocket.receive()
            # verifico que no sea una mala desconexion
            websocket._raise_on_disconnect(msg)
            # verifico si el cliente se quiere desconectar
            if (msg["text"] == "desconexion"):
                ws_players_list.remove(websocket)
                await websocket.send_json("cerrando conexion")
                await websocket.close(reason="cliente pide desconexion")
                break
    except WebSocketDisconnect:
        if websocket in ws_players_list:
            ws_players_list.remove(websocket)


async def broadcast(message: dict):
    for p in ws_players_list:
        await p.send_json(message)
        await p.send_json("reset")


ws_players_list: List[WebSocket] = []


# websocket para sala
@router.websocket('/lobby/{match_id}')
async def websocket_endpoint_lobby(websocket: WebSocket, match_id: int):
    # obtengo el lobby al que se quiere conectar
    lobby = get_lobby(match_id)
    # conecto el ws del cliente a el lobby y aviso a todos que se unio alguien
    # actualizando la cantidad de jugadores
    await lobby.connect(websocket)
    try:
        while True:
            # espero un mensaje
            msg = await websocket.receive()
            # verifico que no sea una mala desconexion
            websocket._raise_on_disconnect(msg)
            # chat
            if (msg["text"] != "desconexion"):
                msg = json.loads(msg["text"])
                mensaje = {"mensaje_chat": {
                    "player_orig": msg["player_orig"],
                    "message": msg["message"], }}
                msg = mensaje
            # verifico si el cliente se quiere desconectar
            elif (msg["text"] == "desconexion"):
                await lobby.disconnect(websocket)
                break
            #
            await lobby.broadcast_lobby(msg)
    except WebSocketDisconnect:
        if websocket in lobby.ws_players:
            lobby.ws_players.remove(websocket)

# websocket para juego


@router.websocket('/game/{match_id}')
async def websocket_endpoint_game(websocket: WebSocket, match_id: int):
    game = get_global_juego(match_id)
    await game.connect_game(websocket)
    try:
        while True:
            msg = await websocket.receive()
            websocket._raise_on_disconnect(msg)
            if (msg["text"] != "desconexion"):
                msg = json.loads(msg["text"])
                mensaje = {"mensaje_chat": {
                    "player_orig": msg["player_orig"],
                    "message": msg["message"], }}
                msg = mensaje
            elif (msg["text"] == "desconexion"):
                await game.disconnect_game(websocket)
                break
            await game.broadcast_global(msg)
    except WebSocketDisconnect:
        if websocket in game.ws_players_game:
            game.ws_players_game.remove(websocket)
