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

# @router.post("/play", status_code=status.HTTP_200_OK)
# async def jugar_carta(match_id: int = Form(), card_id: int = Form(),
#                       player_objective: int = Form(), player_orig: int = Form()):
#     try:
#         juego = get_global_juego(match_id)
#         jugador = get_jugador(player_orig, juego)
#         check_turno(jugador)
#         await jugar_la_carta(juego, card_id, player_objective, player_orig)
#         await juego.broadcast_global("C")
#         descartar_carta(card_id, player_orig, juego)
#         ganador = check_ganador(juego)
#         if ganador:
#             await juego.broadcast_global("K")
#         await juego.mensaje_personal(player_orig, "D")
#         await juego.mensaje_personal(player_orig, "G")
#         return {
#             "carta": card_id,
#             "jugada contra": player_objective,
#             "por": player_orig}
#     except HTTPException as e:
#         error_msg = f"Error: {e.detail}"
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=error_msg
#         )


@router.post("/play/attack", status_code=status.HTTP_200_OK)
async def jugar_ataque(match_id: int = Form(), card_id: int = Form(),
                       player_objective: int = Form(), player_orig: int = Form()):
    try:
        juego = get_global_juego(match_id)
        jugador = get_jugador(player_orig, juego)
        check_turno(jugador)
        validar_jugada(juego, card_id, player_objective, player_orig)
        if check_puedo_defender(juego, card_id, player_objective, player_orig):
            msg = crear_mensaje_de_ataque(jugador, card_id)
            juego.crear_ataque(player_orig, card_id, player_objective)
            await juego.mensaje_personal(player_objective, "J")
            await juego.mensaje_personal_dict(player_objective, {"mensaje_ataque": msg})
            return {"message": "Se creó la solicitud de ataque."}
        else:
            await jugar_la_carta(juego, card_id, player_objective, player_orig)
            await juego.broadcast_global("C")
            descartar_carta(card_id, player_orig, juego)
            if check_ganador(juego):
                await juego.broadcast_global("K")
            await juego.mensaje_personal(player_orig, "D")
            await juego.mensaje_personal(player_orig, "G")
            return {"message": "Se jugó el ataque."}
    except HTTPException as e:
        error_msg = f"Error: {e.detail}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )


@router.post("/play/defense", status_code=status.HTTP_200_OK)
async def jugar_defensa(match_id: int = Form(), card_id: int = Form(),
                        player_orig: int = Form()):
    try:
        juego = get_global_juego(match_id)
        #####
        juego.solicitud_ataque.carta_defensor = card_id
        jugador_ataque = juego.solicitud_ataque.atacante
        carta_ataque = juego.solicitud_ataque.carta_atacante
        jugador_defensa = juego.solicitud_ataque.defensor
        carta_defensa = juego.solicitud_ataque.carta_defensor

        if card_id != 0:
            validar_carta(card_id, player_orig, juego)
        check_posibilidad_defensa(card_id, juego)
        #
        if card_id == 0:
            await jugar_la_carta(juego, carta_ataque,
                                 jugador_defensa.id, jugador_ataque.id)
            juego.responder_ataque(player_orig, card_id)
            await juego.broadcast_global("C")
        else:
            carta_ataque_nombre = get_name_carta(carta_ataque)
            carta_defensa_nombre = get_name_carta(carta_defensa)
            msg = {
                "mensaje": jugador_ataque.name +
                " jugó " +
                carta_ataque_nombre +
                " contra " +
                jugador_defensa.name +
                ", pero se defendió con " +
                carta_defensa_nombre}
            await juego.broadcast_global({"carta_id": card_id,
                                          "mensaje": msg["mensaje"]})
            juego.responder_ataque(player_orig, card_id)
            juego.robar_carta_no_panico(jugador_defensa)
        ###
        ganador = check_ganador(juego)
        if ganador:
            await juego.broadcast_global("K")
        await juego.mensaje_personal(player_orig, "D")
        await juego.mensaje_personal(jugador_ataque.id, "D")
        await juego.mensaje_personal(jugador_ataque.id, "G")
        if card_id == 0:
            return {"message": "Se completó el ataque."}
        else:
            return {"message": "Se completó la defensa."}
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
        await juego.mensaje_personal(player_id, "D")
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
        check_carta_habilitada(card_id, jugador_orig, jugador_objetivo)

        check_objetive_is_next(jugador_objetivo, juego)
        check_obstaculo(player_orig, jugador_objetivo.id, juego)

        juego.crear_intercambio(player_orig, card_id, jugador_objetivo.id)
        await juego.mensaje_personal(jugador_objetivo.id, "H")

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

        check_carta_habilitada(card_id, jugador_orig, jugador_objetivo)
        juego.responder_intercambio(player_orig, card_id)
        await juego.mensaje_personal(player_orig, "D")
        await juego.mensaje_personal(jugador_objetivo.id, "D")
        ganador = check_ganador(juego)
        if ganador:
            await juego.broadcast_global("K")

        await juego.mensaje_personal(jugador_orig.id, "E")
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
