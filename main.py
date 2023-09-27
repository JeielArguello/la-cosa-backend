from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from models.database import create_db
from models.card_init import create_cards
from fastapi.middleware.cors import CORSMiddleware
from endpoints.match import router as router_match
from models.match_models import all_matchs
from endpoints.user import *
from endpoints.user import router as user_router

app = FastAPI()

app.include_router(router_match)
app.include_router(user_router, prefix = "/user")

@app.on_event("startup")
def startup_db():
    create_db()
    create_cards()



@app.get("/")
async def root():
    return {"message": "Hello there!"}


"""
No implementado completamente, ignorar
"""
@app.websocket('/ws/{match_id}')
async def websocket_endpoint(websocket: WebSocket, match_id: int):
    for p in all_matchs:
        if p.id_Match == match_id:
            match = p
         
    await match.connect(websocket)

    try:
        while True:
            msg = await websocket.receive()
            await match.broadcast(msg)
    except WebSocketDisconnect:
        match.disconnect(websocket)
        await match.broadcast(f"Client left the chat")

    await match.disconnect(websocket)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)    
    
