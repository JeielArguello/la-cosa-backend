from fastapi import APIRouter,HTTPException,status,WebSocket
from models.match_models import CreateMatchRequest,JoinMatchRequest,Match,all_matchs
from models.crud import init_match,get_exist_user


router = APIRouter(prefix='/match')
#hacer test
@router.post('/create',status_code=status.HTTP_201_CREATED)
async def match_create(match_:CreateMatchRequest):
    #validar pedidio
    if get_exist_user(match_.id_usuario_creador):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario ya ingresado en una partida"
        )
    if match_.num_min_jugadores < 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Numero minimo de jugadores menor a 4"
        )
    if match_.num_max_jugadores > 11:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Numero maximo de jugadores mayor a 11"
        )
    #crear instancia
    match = Match(match_)
    all_matchs.append(match)
    #inicializar en la base de datos
    match.id_Match=init_match(match_)
    
    return {'match_id' : match.id_Match}

#hacer test dsp
@router.post('/join')
async def match_join(match_:JoinMatchRequest,ws:WebSocket):
    #validar datos
    for p in all_matchs:
        if p.id_Match == match_.match_id :
             match_join = p

    match_join.add_player()
    #actualizar base de datos
    return { 'user_id' : match_.id_player,'match_id' : match_join.id_Match}

@router.get('/list')
async def match_list(): 
    list_rooms=[]
    for room in all_matchs:
        list_rooms.append({'id_room': room.id_Match,'name_room': room.name, 'players_amount':room.player_amount})  

    return list_rooms