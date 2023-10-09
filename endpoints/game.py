from fastapi import HTTPException, Body
from fastapi import APIRouter, Form, HTTPException, status, WebSocket
# from models.match_models import Match, all_matchs
from models.crud import *
from models.database_utils import *
from utils.match_utils import *
from models.match_models import *
from logic.game import Juego
from logic.player import JugadorPartida
from logic.action_effects import play_lanzallamas
##########
from endpoints.match import global_juegos
##########
router = APIRouter()

######
# Robar Carta
######


@router.post('/pick')
async def pick_a_card_from_deck(match_id: int = Form(), player_id: int = Form()):
    juego = get_global_juego(match_id)
    for jugador_en_partida in juego.jugadores_en_partida:
        if jugador_en_partida.id == player_id:
            jugador = jugador_en_partida
    robar_carta(juego, jugador)


def robar_carta(juego: Juego, jugador: JugadorPartida):
    if len(juego.mazo) == 0:
        raise HTTPException(
            status_code=400,
            detail="El mazo esta vacio")
    carta_id = juego.mazo.pop()
    jugador.agregar_carta(carta_id)

######
# Jugar carta
######


@router.post('/play')
async def jugar_carta(match_id: int = Form(), card_id: int = Form(), player_objective: int = Form(), player_orig: int = Form()):
    juego = get_global_juego(match_id)
    resultado = jugar_la_carta(juego, card_id, player_objective, player_orig)
    # if descartar_carta(card_id, player_orig, match_id):
    return {"carta": card_id, "jugada contra": player_objective, "por": player_orig}
    # return {"error al jugar la carta": card_id, "contra": player_objective, "por": player_orig}


def jugar_la_carta(juego: Juego, card_id: int, player_objective: int, player_orig: int):
    if card_id in [22, 23, 24, 25, 26]:
        play_lanzallamas(player_orig, player_objective, juego)
        return True
    else:
        return False


@db_session
def descartar_carta(card_id: int, player_orig: int, match_id: int):
    juego = select(j for j in Partida if j.id == match_id).first()
    if juego:
        juego.mazo_descarte.append(card_id)
        juego.jugadores_en_partida[player_orig].cartas.pop(card_id)
        return True
    return False
######
# Descartar carta
######


# @router.post('/discard')
# async def descartar_carta(match_id: int = Form(), card_id: int = Form(), player_id: int = Form()):
#     juego = get_global_juego(match_id)
#     if descartar_carta(card_id, player_id, match_id):
#         return {"carta": card_id, "Descartada por": player_id}

######
# Finalizar Partida
######


@router.post('/finish')
async def finish_match(match_id: int = Form()):
    try:
        juego = get_global_juego(match_id)
        result = finalizar_partida(juego)
        if result != {"mensaje": "La partida aún no ha finalizado", "ganador": 0}:
            delete_global_juego(match_id)
        return result
    except HTTPException as e:
        error_msg = f"Error: {e.detail}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )


def finalizar_partida(juego: Juego):
    if len(juego.jugadores_en_partida) == 1:
        ganador = juego.jugadores_en_partida.pop()
        ganador_id = ganador.id
        return {"mensaje": "La partida ha finalizado", "ganador": ganador_id}
    elif len(juego.jugadores_en_partida) == 0:
        return {"mensaje": "partida sin jugadores", "ganador": 0}
    else:
        return {"mensaje": "La partida aún no ha finalizado", "ganador": 0}


######
# Funcion que obtiene juego
######
# global_juegos: list[Juego]


def get_global_juego(match_id: int) -> Juego:
    result = None
    for juego in global_juegos:
        if juego.partida_id == match_id:
            result = juego
    if(result is None):
        raise HTTPException(
            status_code=400, detail="No se pudo acceder al juego")
    return result


def delete_global_juego(match_id):
    result = None
    for juego in global_juegos:
        if juego.partida_id == match_id:
            result = juego
    if(result is None):
        raise HTTPException(
            status_code=400, detail="No se puedo borrar el juego")
    global_juegos.remove(result)
