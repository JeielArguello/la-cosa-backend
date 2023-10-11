from fastapi import HTTPException, Body
from fastapi import APIRouter, Form, HTTPException, status, WebSocket
# from models.match_models import Match, all_matchs
from models.crud import *
from models.database_utils import *
##########
from logic.game import Juego
# from endpoints.game import get_global_juego

global_juegos: list[Juego] = []
##########

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
        # crear instancia
        partida = crear_partida(id_usuario_creador, id_name, contraseña,
                                num_max_jugadores, num_min_jugadores)
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
                     user_id: int = Form()):
    try:
        # validar datos
        validar_entrada_partida(user_id, match_id)
        # actualizar base de datos
        update_add_player(user_id, match_id)
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
        # juego.crear_mazo
        # juego.repartir_cartas
    global_juegos.append(juego)
    print(juego.posiciones)
    # ##########
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

# Game state


@router.get("/game/state/{match_id}")
async def get_game_state(match_id: int):
    try:
        juego = get_global_juego(match_id)
        result = get_status_game(juego)
        return result
    except HTTPException as e:
        error_msg = f"Error: {e.detail}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )


def get_status_game(juego: Juego):
    posiciones = juego.posiciones
    sentido = juego.sentido
    jugadores = get_jugadores_match(juego.partida_id)
    response = {'posiciones': posiciones,
                'jugadores': jugadores, 'sentido': sentido}
    return response


def get_global_juego(match_id: int) -> Juego:
    result = None
    for juego in global_juegos:
        if juego.partida_id == match_id:
            result = juego
    if(result is None):
        raise HTTPException(
            status_code=400, detail="No se pudo acceder al juego")
    return result

# falta mover las funciones sin importaciones circulares T_T

# Player state


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


def get_status_player(juego: Juego, player_id: int):
    jugador = None
    for j in juego.jugadores_en_partida:
        if j.id == player_id:
            jugador = j
    if jugador is None:
        raise HTTPException(
            status_code=400, 
            detail="El jugador no se encuentra en la partida")
    mano = jugador.cartas
    muerto = jugador.muerto
    la_cosa = jugador.la_cosa
    humano = jugador.humano
    infectado = jugador.infectado
    response = {'mano': mano, 'muerto': muerto, 'la_cosa': la_cosa,
                'humano': humano, 'infectado': infectado}
    return response
