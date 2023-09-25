from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from models.database import create_db
from models.card_init import create_cards
from models.match import *
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()


@app.on_event("startup")
def startup_db():
    create_db()
    create_cards()


@app.get("/")
async def root():
    return {"message": "Hello there!"}

#hacer test
@app.post('/match/create')
async def match_create(match_:CreateMatchRequest):
    #validar pedidio
    match = Match(match_)
    all_matchs.append(match)
    match.id_Match=len(all_matchs)-1
    #iniciar la partida en bases de datos
    return {'match_id' : match.id_Match}

#hacer test dsp
@app.post('/match/join')
async def match_join(match_:JoinMatchRequest,ws:WebSocket):
    #validar datos
    for p in all_matchs:
        if p.id_Match == match_.match_id :
             match_join = p

    match_join.add_player()
    #actualizar base de datos
    return { 'user_id' : match_.id_player,'match_id' : match_join.id_Match}

@app.websocket('/ws/{match_id}')
async def websocket_endpoint(websocket: WebSocket, match_id: int):
    match = all_matchs[match_id]
    await match.connect(websocket)

    try:
        while True:
            msg = await websocket.receive()
            await match.broadcast(msg)
    except WebSocketDisconnect:
        match.disconnect(websocket)
        await match.broadcast(f"Client left the chat")

    await match.disconnect(websocket)


@app.get('/match/list')
async def match_list(): 
    list_matchs=[]
    for match in all_matchs:
        list_matchs.append({'id_match': match.id_Match,'name_match': match.name, 'players_amount':match.player_amount})  

    return list_matchs



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)    
    
