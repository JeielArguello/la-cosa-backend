from fastapi import HTTPException, Body
from fastapi import APIRouter, Form, HTTPException, status, WebSocket
# from models.match_models import Match, all_matchs
from models.crud import *
from models.database_utils import *
from utils.match_utils import *
from models.lobby_models import *
#from endpoints.websocket import broadcast

router = APIRouter()


@router.post('/create')
async def match_create(id_usuario_creador: int = Form(),
                       id_name: str = Form(),
                       contraseña: str = Form(default=None),
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
        await broadcast("A")
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


@router.post('/join')
async def match_join(match_id: int = Form(),
                     user_id: int = Form(),
                     contrasena: str = Form(default=None)):
    try:
        # validar datos
        validar_entrada_partida(user_id, match_id,contrasena)
        # actualizar base de datos
        update_add_player(user_id, match_id)
        estado = get_estado_partida(match_id)
        await broadcast("A")
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


@router.post("/start")
async def iniciar_partida(user_id: int = Form(), match_id: int = Form()):
    database_utils_iniciar_partida(match_id, user_id)
    # ##########
    with db_session:
        partida = get_match(match_id)
        creador = partida.id_jugador_creador
        jugadores_id = []
        for jugador in partida.jugadores:
            id = jugador.id
            jugadores_id.append(id)
        cantidad_jugadores = len(partida.jugadores)
        juego = Juego(partida.id, cantidad_jugadores, creador, jugadores_id)
    global_juegos.append(juego)
    print(juego.posiciones)
    # ##########
    await broadcast("A")
    return {"message": "Se inició con éxito la partida."}


@router.get("/state/{match_id}")
async def get_state(match_id: int):
    try:
        estado = get_estado_partida(match_id)
        return estado
    except HTTPException as e:
        error_msg = f"Error: {e.detail}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )


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

    
   
@router.get('/list')
async def match_list():
    try:
        list_partida = listar_partidas()
        return list_partida

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
