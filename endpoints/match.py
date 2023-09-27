from fastapi import APIRouter, Form,HTTPException,status,WebSocket
from models.match_models import Match,all_matchs
from models.crud import *
from models.database_utils import *


router = APIRouter(prefix='/match')
#hacer test
@router.post('/create',status_code=status.HTTP_201_CREATED)
async def match_create(id_usuario_creador: int = Form(),
                        id_name: str = Form(),
                        contraseña: str = Form(),
                        num_max_jugadores: int = Form(),
                        num_min_jugadores: int = Form()):
    #validar pedidio
    match_dict = {
        "id_usuario_creador": id_usuario_creador,
        "id_name":  id_name,
        "contraseña": contraseña,
        "num_max_jugadores": num_max_jugadores,
        "num_min_jugadores" : num_min_jugadores
    }
    if not get_exist_user(match_dict["id_usuario_creador"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario no existe"
        )
    if get_exist_user_in_game(match_dict["id_usuario_creador"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario ya ingresado en una partida"
        )
    if match_dict["num_min_jugadores"] < 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Numero minimo de jugadores menor a 4"
        )
    if match_dict["num_max_jugadores"] > 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Numero maximo de jugadores mayor a 11"
        )
    #crear instancia
    match = Match(match_dict)
    all_matchs.append(match)
    #inicializar en la base de datos
    match.id_Match=init_match(match_dict)
    return {"match_id" : match.id_Match}

