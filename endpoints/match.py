from fastapi import HTTPException, Body
from fastapi import APIRouter, Form, HTTPException, status
from models.crud import *
from models.database_utils import *
from utils.match_utils import *
from models.lobby_models import *
#from endpoints.websocket import broadcast

router = APIRouter()


@router.post('/create')
async def match_create(id_usuario_creador: int = Form(),
                       id_name: str = Form(),
                       contraseña: str = Form(),
                       num_max_jugadores: int = Form(),
                       num_min_jugadores: int = Form()
                       ):
    try:
        # validar pedidio
        validar_partida(id_usuario_creador,
                        num_max_jugadores, num_min_jugadores)
        # crear partida en base de datos
        partida = crear_partida(id_usuario_creador, id_name, contraseña,
                                num_max_jugadores, num_min_jugadores)
        
        #crear instancia de partida
        lobby = Lobby(id_usuario_creador, id_name, contraseña,
                                num_max_jugadores, num_min_jugadores,partida["id_partida"])
        all_lobby.append(lobby)
        return partida
    except ValueError as ve:
        error_msg = f"Error: {ve}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    except HTTPException as e:
        error_msg = f"Error: {e.detail}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )


@router.post("/start")
async def iniciar_partida(user_id: int = Form(), match_id: int = Form()):
    database_utils_iniciar_partida(match_id, user_id)
    ##########
    partida = get_match(match_id)
    jugadores_id = []
    for jugador in partida.jugadores:
        id = jugador.id
        jugadores_id.append(id)

    juego = Juego(partida.id, len(partida.jugadores), user_id, jugadores_id)
    global_juegos.append(juego)
    ##########
    return {"message": "Se inició con éxito la partida."}


@router.get("/state/{match_id}")
async def get_state(match_id: int):
    estado = get_estado_partida(match_id)
    return estado


@router.post('/join')
async def match_join(match_id: int = Form(),
                     user_id: int = Form()):
    try:
        # validar datos
        validar_entrada_partida(user_id, match_id)
        # actualizar base de datos
        update_add_player(user_id, match_id)
        lobby = get_lobby(match_id)
        lobby.add_player(user_id)

        estado = get_estado_partida(match_id)
        return estado

    except ValueError as ve:
        error_msg = f"Error: {ve}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    except HTTPException as e:
        error_msg = f"Error: {e.detail}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    
   
