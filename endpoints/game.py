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
    try:
        juego = get_global_juego(match_id)
        jugador = get_jugador(player_id, juego)
        check_turno(jugador)
        check_cantidad_cartas(jugador)
        carta = robar_carta(juego, jugador)
        await juego.broadcast_global("C")
        await juego.mensaje_personal(player_id, "D")
        await juego.mensaje_personal(player_id, "F")

        
        return {'card_id': carta}
    except HTTPException as e:
        error_msg = f"Error: {e.detail}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )


######
# Jugar carta
######


@router.post("/play", status_code=status.HTTP_200_OK)
async def jugar_carta(match_id: int = Form(), card_id: int = Form(),
                      player_objective: int = Form(), player_orig: int = Form()):
    try:
        juego = get_global_juego(match_id)
        jugador = get_jugador(player_orig, juego)
        check_turno(jugador)
        await jugar_la_carta(juego, card_id, player_objective, player_orig)
        await juego.broadcast_global("C")
        descartar_carta(card_id, player_orig, juego)
        ganador = check_ganador(juego)
        if ganador:
            await juego.broadcast_global("K")
        await juego.mensaje_personal(player_orig,"D")
        await juego.mensaje_personal(player_orig, "G")
        return {
            "carta": card_id,
            "jugada contra": player_objective,
            "por": player_orig}
    except HTTPException as e:
        error_msg = f"Error: {e.detail}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )


######
# Descartar carta
######


@router.post("/discard")
async def endpoint_descartar_carta(match_id: int = Form(),
                                   card_id: int = Form(), player_id: int = Form()):
    try:
        juego = get_global_juego(match_id)
        jugador = juego.get_jugador(player_id)
        check_turno(jugador)
        descartar_carta(card_id, player_id, juego)
        await juego.mensaje_personal(player_id,"D")
        await juego.mensaje_personal(player_id, "G")
        return {"carta descartada": card_id}
    except HTTPException as e:
        error_msg = f"Error: {e.detail}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )


######
# Intercambiar carta
######


@router.post("/swap-request")
async def swap_request(match_id: int = Form(), card_id: int = Form(), player_orig: int = Form()):
    try:
        juego = get_global_juego(match_id)
        jugador_orig = juego.get_jugador(player_orig)
        check_turno(jugador_orig)
        jugador_objetivo = juego.get_jugador_siguiente_turno()
        check_carta_habilitada(card_id,jugador_orig,jugador_objetivo)

        check_objetive_is_next(jugador_objetivo,juego)
        check_obstaculo(player_orig,jugador_objetivo.id,juego)

        juego.crear_intercambio(player_orig,card_id,jugador_objetivo.id)
        await juego.mensaje_personal(jugador_objetivo.id,"H")
        
        return {"message": "se creo la solicitud de intercambio"}
    except HTTPException as e:
        error_msg = f"Error: {e.detail}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

@router.post("/swap-response")
async def swap_response(match_id: int = Form(), card_id: int = Form(), player_orig: int = Form()):
    try:
        juego = get_global_juego(match_id)
        jugador_orig = juego.get_jugador(player_orig)
        jugador_objetivo = juego.get_jugador_en_turno()
        
        juego.terminar_turno()
        juego.avanzar_turno()
        
        check_carta_habilitada(card_id,jugador_orig,jugador_objetivo)
        juego.responder_intercambio(player_orig, card_id)
        await juego.mensaje_personal(player_orig,"D")
        await juego.mensaje_personal(jugador_objetivo.id,"D")
        ganador = check_ganador(juego)
        if ganador:
            await juego.broadcast_global("K")

        await juego.mensaje_personal(jugador_orig.id,"E")
        await juego.broadcast_global("C")
        return {"message": "se completo el intercambio"}
    except HTTPException as e:
        error_msg = f"Error: {e.detail}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

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
        await juego.broadcast_global({'resultados': result})
        return result
    except HTTPException as e:
        error_msg = f"Error: {e.detail}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

@router.post('/finish/thething')
async def finish_match_thething(match_id: int = Form(),player_id: int = Form()):
    try:
        juego = get_global_juego(match_id)
        jugador = juego.get_jugador(player_id)
        check_la_cosa(jugador)
        result = finalizar_juego(juego)
        delete_global_juego(match_id)
        delete_match(match_id)
        await juego.broadcast_global({'resultados': result})
        return result
    except HTTPException as e:
        error_msg = f"Error: {e.detail}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
