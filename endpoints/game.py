from fastapi import HTTPException, Body
from fastapi import APIRouter, Form, HTTPException, status
from models.crud import *
from models.database_utils import *
from utils.match_utils import *
from models.lobby_models import *
from models.game import robar_carta
##########
from utils.game_utils import *
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
    carta = robar_carta(juego, jugador)
    return {'card_id': carta}


######
# Jugar carta
######


@router.post("/play", status_code=status.HTTP_200_OK)
async def jugar_carta(match_id: int = Form(), card_id: int = Form(),
                      player_objective: int = Form(), player_orig: int = Form()):
    juego = get_global_juego(match_id)
    resultado = jugar_la_carta(juego, card_id,
                               player_objective, player_orig)

    await juego.broadcast_global("C")

    # if descartar_carta(card_id, player_orig, juego):
    return {"carta": card_id, "jugada contra": player_objective, "por": player_orig}
    # return {"error al jugar la carta": card_id, "contra": player_objective, "por": player_orig}

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
        result = finalizar_juego(juego)
        delete_global_juego(match_id)
        delete_match(match_id)
        # await broadcast_game({resultados:result})
        return result
    except HTTPException as e:
        error_msg = f"Error: {e.detail}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
