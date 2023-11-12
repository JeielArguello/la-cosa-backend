from fastapi import HTTPException
from fastapi import APIRouter, Form, HTTPException, status
from endpoints.websocket import broadcast
from models.crud import *
from models.database_utils import *
from models.game import mazo_vacio
from utils.game_utils import get_global_juego, get_status_game, get_status_player
from utils.match_utils import *
from models.lobby_models import Lobby, delete_lobby
from models.constants import *



router = APIRouter()

######
# Crear Partida
######


@router.post('/create')
async def match_create(id_usuario_creador: int = Form(),
                       id_name: str = Form(),
                       contrasena: str = Form(default=None),
                       num_max_jugadores: int = Form(),
                       num_min_jugadores: int = Form()
                       ):
    try:
        # validar pedidio
        validar_partida(id_usuario_creador,
                        num_max_jugadores, num_min_jugadores)
        # crear instancia
        partida = crear_partida(id_usuario_creador, id_name, contrasena,
                                num_max_jugadores, num_min_jugadores)
        # crear instancia de partida
        lobby = Lobby(
            id_usuario_creador,
            id_name,
            contrasena,
            num_max_jugadores,
            num_min_jugadores,
            partida["id_partida"])
        all_lobby.append(lobby)
        await broadcast(CAMBIO_LISTAR_PARTIDA)
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

######
# Unirse Partida
######


@router.post('/join')
async def match_join(match_id: int = Form(),
                     user_id: int = Form(),
                     contrasena: str = Form(default=None)):
    try:
        # validar datos
        validar_entrada_partida(user_id, match_id, contrasena)
        # actualizar base de datos
        update_add_player(user_id, match_id)
        estado = get_estado_partida(match_id)
        # actualizo el lobby
        lobby = get_lobby(match_id)
        lobby.add_player(user_id)
        await broadcast(CAMBIO_LISTAR_PARTIDA)
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

######
# Abandonar Partida
######


@router.post("/exit")
async def abandonar_partida(id_jugador: int = Form(), match_id: int = Form()):
    try:
        lobby = get_lobby(match_id)
        if (id_jugador == lobby.id_usuario_creador):
            delete_match(match_id)
            await broadcast(CAMBIO_LISTAR_PARTIDA)
            if (lobby.cantidad_jugadores > 1):
                await lobby.broadcast_lobby(ABANDONO_CREADOR)
            delete_lobby(match_id)
        else:
            models_crud_eliminar_jugador_no_creador_de_pratida_sin_inicializar(
                id_jugador, match_id)
            lobby.remove_player(id_jugador)
            await lobby.broadcast_lobby(CAMBIO_ESTADO_LOBBY)
            await broadcast(CAMBIO_LISTAR_PARTIDA)
    except HTTPException as e:
        error_msg = f"Error: {e.detail}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )


######
# Iniciar Partida
######


@router.post("/start")
async def iniciar_partida(user_id: int = Form(), match_id: int = Form()):
    try:
        database_utils_iniciar_partida(match_id, user_id)
        lobby = get_lobby(match_id)
        await lobby.init_game()
        # broadcast a los jugadores para que listen las partidas
        await broadcast(CAMBIO_LISTAR_PARTIDA)
        # broadcast a los jugadores del lobby para que inicien el juego
        await lobby.broadcast_lobby(PARTIDA_INICIADA)
        return {"message": "Se inició con éxito la partida."}
    except HTTPException as e:
        error_msg = f"Error: {e.detail}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

######
# Listar Partida
######


@router.get('/list')
async def match_list():
    try:
        list_partida = listar_partidas()
        return list_partida
    # except ValueError as ve:
    #     error_msg = f"Error: {ve}"
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail=error_msg
    #     )
    except HTTPException as e:
        error_msg = f"Error: {e.detail}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )


######
# Estado Juego
######
@router.get("/game/state/{match_id}")
async def get_game_state(match_id: int):
    try:
        juego = get_global_juego(match_id)
        mazo_vacio(juego)
        result = get_status_game(juego)
        return result
    except HTTPException as e:
        error_msg = f"Error: {e.detail}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

######
# Estado Jugador
######


@router.get("/player/state/{match_id}/{player_id}")
async def get_player_state(match_id: int, player_id: int):
    try:
        juego = get_global_juego(match_id)
        result = get_status_player(juego, player_id)
        return result
    except HTTPException as e:
        error_msg = f"Error: {e.detail}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )


######
# Estado Partida
######


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
