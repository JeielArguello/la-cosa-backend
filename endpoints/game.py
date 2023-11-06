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
        if check_carta_panico(juego):
            carta = juego.mazo.pop()
            await jugar_panico(carta, juego)
            juego.mazo_descarte.append(carta)
            await juego.broadcast_global("C")

            jugador_proximo = juego.get_jugador_siguiente_turno()
            if(not jugador_proximo.get_muerto() and is_obstaculo(jugador.id, jugador_proximo.id, juego)):
                juego.terminar_turno()
                juego.avanzar_turno()

                await juego.mensaje_personal(jugador_proximo.id, "E") 
            else:
                await juego.mensaje_personal(player_id, "G")
            return {'card_id': carta}
        else:
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
@router.post("/play/attack", status_code=status.HTTP_200_OK)
async def jugar_ataque(match_id: int = Form(), card_id: int = Form(),
                       player_objective: int = Form(), player_orig: int = Form()):
    try:
        juego = get_global_juego(match_id)
        jugador = get_jugador(player_orig, juego)
        objetivo = juego.get_jugador(player_objective)
        seduccion = objetivo.afectado_seduccion
        check_turno(jugador)
        validar_jugada(juego, card_id, player_objective, player_orig)
        jugador_proximo = juego.get_jugador_siguiente_turno()
        if (player_objective == jugador_proximo.id and is_hacha(card_id)):
            check_obstaculo(player_orig,jugador_proximo.id,juego)
        jugador_anterior = juego.get_jugador_anterior_turno()
        if (player_objective == jugador_anterior.id and is_hacha(card_id)):
            check_obstaculo(player_orig,jugador_anterior.id,juego)
        
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
            if not juego.cartas_determinacion:    
                if(player_orig == player_objective or card_id in [50, 51, 52, 53, 54, 55, 56, 57, 58, 59]):
                    jugador_proximo = juego.get_jugador_siguiente_turno()                      
                if(not jugador_proximo.get_muerto() and is_obstaculo(jugador.id, jugador_proximo.id, juego) and not seduccion ):
                    juego.terminar_turno()
                    juego.avanzar_turno()

                    await juego.mensaje_personal(jugador_proximo.id, "E")
                else:    
                    await juego.mensaje_personal(jugador.id, "G")

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
            juego.agregar_log(msg["mensaje"])
            juego.responder_ataque(player_orig, card_id)
            juego.robar_carta_no_panico(jugador_defensa)
        ###
        ganador = check_ganador(juego)
        if ganador:
            await juego.broadcast_global("K")
        await juego.mensaje_personal(player_orig, "D")
        await juego.mensaje_personal(jugador_ataque.id, "D")
        
        jugador_proximo = juego.get_jugador_siguiente_turno()
        if(is_obstaculo(jugador_ataque.id, jugador_proximo.id, juego)):
            juego.terminar_turno()
            juego.avanzar_turno()

            await juego.mensaje_personal(jugador_proximo.id, "E")
        else:    
            await juego.mensaje_personal(jugador_ataque.id, "G")
        if card_id == 0:
            return {"message": "Se completó el ataque."}
        else:
            return {"message": "Se completó la defensa."}
        # await juego.mensaje_personal(player_orig,"D")
        # return {
        #     "carta": card_id,
        #     "jugada contra": player_objective,
        #     "por": player_orig}
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

        jugador_objetivo = juego.get_jugador_siguiente_turno()

        if(is_obstaculo(jugador.id, jugador_objetivo.id, juego)):
            juego.terminar_turno()
            juego.avanzar_turno()

            await juego.mensaje_personal(jugador_objetivo.id, "E")
        else:    
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
        jugador_objetivo_index = next((i for i, jugador in enumerate(
            juego.jugadores_en_partida) if jugador.afectado_seduccion), None)
        if not jugador_objetivo_index is None:
            jugador_objetivo = juego.jugadores_en_partida[jugador_objetivo_index]
            #jugador_orig.afectado_seduccion = False
        else:
            jugador_objetivo = juego.get_jugador_siguiente_turno()
            check_objetive_is_next(jugador_objetivo, juego)
        check_carta_habilitada(card_id, jugador_orig, jugador_objetivo)
        if not jugador_objetivo.afectado_seduccion:
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
        check_carta_habilitada(card_id, jugador_orig, jugador_objetivo)
        juego.terminar_turno()
        juego.avanzar_turno()

        juego.responder_intercambio(player_orig, card_id)
        await juego.mensaje_personal(player_orig, "D")
        await juego.mensaje_personal(jugador_objetivo.id, "D")
        ganador = check_ganador(juego)
        if ganador:
            await juego.broadcast_global("K")
        if jugador_orig.afectado_seduccion:
            jugador = juego.get_jugador_en_turno().id
            await juego.mensaje_personal(jugador, "E")
            jugador_orig.afectado_seduccion = False
        else:
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


@router.post('/finish/thething')
async def finish_match_thething(match_id: int = Form(), player_id: int = Form()):
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

######
# Seleccionar, Determinacion
######


@router.post("/play/determination")
async def seleccionar_carta_determinacion(match_id: int = Form(),
                                          card_id: int = Form(), player_id: int = Form()):
    try:
        juego = get_global_juego(match_id)
        jugador = juego.get_jugador(player_id)
        check_turno(jugador)
        agregar_carta_determinacion(card_id, player_id, juego)
        await juego.mensaje_personal(player_id, "D")
        await juego.mensaje_personal(player_id, "F")
        return {"carta elegida": card_id}
    except HTTPException as e:
        error_msg = f"Error: {e.detail}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

#################
#GET LOGS 
#################

@router.get("/log/{match_id}")
async def get_logs_del_juego(match_id: int):
    try:
        juego = get_global_juego(match_id)
        logs = juego.get_logs()
        return {
            "logs":logs,
        }
    except HTTPException as e:
        error_msg = f"Error: {e.detail}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )