from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from models.match_models import all_matchs
from endpoints.match import iniciar_partida 


router = APIRouter()


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
                await iniciar_partida(1,1)
                await match.broadcast("se inicio la partida")
             await match.broadcast(msg)
    except WebSocketDisconnect:
         match.disconnect(websocket)
         await match.broadcast(f"Client left the chat")

    await match.disconnect(websocket)
