# from fastapi import FastAPI, WebSocket, WebSocketDisconnect

# """
# No implementado completamente, ignorar
# """


# @app.websocket('/ws/{match_id}')
# async def websocket_endpoint(websocket: WebSocket, match_id: int):
#     for p in all_matchs:
#         if p.id_Match == match_id:
#             match = p

#     await match.connect(websocket)

#     try:
#         while True:
#             msg = await websocket.receive()
#             await match.broadcast(msg)
#     except WebSocketDisconnect:
#         match.disconnect(websocket)
#         await match.broadcast(f"Client left the chat")

#     await match.disconnect(websocket)
