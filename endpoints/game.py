from fastapi import HTTPException, Body
from fastapi import APIRouter, Form, HTTPException, status
from logic.defense_effects import defense_aterrador, defensa_no_gracias
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

            if not is_vuelta_y_vuelta(carta):
                jugador_proximo = juego.get_jugador_siguiente_turno()
                if not jugador_proximo.get_muerto() and juego.is_obstaculo(jugador.id, jugador_proximo.id) :
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
            await mostrar_cartas_cuarentena(jugador, carta, juego, 1)

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
        seduccion = objetivo.get_efecto_seduccion()
        check_turno(jugador)
        validar_jugada(juego, card_id, player_objective, player_orig)
        jugador_proximo = juego.get_jugador_siguiente_turno()
        if (player_objective == jugador_proximo.id and not is_hacha(card_id)):
            check_obstaculo(player_orig, jugador_proximo.id, juego)
        jugador_anterior = juego.get_jugador_anterior_turno()
        if (player_objective == jugador_anterior.id and not is_hacha(card_id)):
            check_obstaculo(player_orig, jugador_anterior.id, juego)
        if check_puedo_defender(juego, card_id, player_objective, player_orig) and not is_seduccion(card_id):
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
                if (player_orig == player_objective or card_id in [50, 51, 52, 53, 54, 55, 56, 57, 58, 59]):
                    jugador_proximo = juego.get_jugador_siguiente_turno()
                if (not jugador_proximo.get_muerto() and juego.is_obstaculo(jugador.id, jugador_proximo.id) and not is_seduccion(card_id)):
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
        jugador_ataque = juego.solicitud_ataque.atacante
        carta_ataque = juego.solicitud_ataque.carta_atacante
        jugador_defensa = juego.get_jugador(player_orig)

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
            if is_card_defense(card_id) and not is_seduccion(carta_ataque):
                await defenderse_de_intercambio(juego, card_id, jugador_defensa, jugador_ataque)
            else:
                await jugar_la_carta(juego, card_id,
                                     jugador_defensa.id, jugador_ataque.id)
            juego.responder_ataque(player_orig, card_id)
        ###
        ganador = check_ganador(juego)
        if ganador:
            await juego.broadcast_global("K")
        await juego.mensaje_personal(player_orig, "D")
        await juego.mensaje_personal(jugador_ataque.id, "D")

        jugador_proximo = juego.get_jugador_siguiente_turno()
        if (juego.is_obstaculo(jugador_ataque.id, jugador_proximo.id) and not is_fallaste(card_id)):
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
        jugador = get_jugador(player_id, juego)
        check_turno(jugador)
        descartar_carta(card_id, player_id, juego)
        await juego.mensaje_personal(player_id, "D")
        jugador_objetivo = juego.get_jugador_siguiente_turno()
        if (juego.is_obstaculo(jugador.id, jugador_objetivo.id)):
            juego.terminar_turno()
            juego.avanzar_turno()
            await juego.mensaje_personal(jugador_objetivo.id, "E")
        else:
            await juego.mensaje_personal(player_id, "G")
        await mostrar_cartas_cuarentena(jugador, card_id, juego, 2)
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
            juego.jugadores_en_partida) if jugador.get_efecto_seduccion()), None)
        if not jugador_objetivo_index is None:
            jugador_objetivo = juego.jugadores_en_partida[jugador_objetivo_index]
        else:
            jugador_objetivo = juego.get_jugador_siguiente_turno()
            check_objetive_is_next(jugador_objetivo, juego)
        check_carta_habilitada(card_id, jugador_orig, jugador_objetivo)
        if not jugador_objetivo.get_efecto_seduccion() and not jugador_objetivo.get_cuartena():
            check_obstaculo(player_orig, jugador_objetivo.id, juego)

        juego.crear_intercambio(player_orig, card_id, jugador_objetivo.id)
        await juego.mensaje_personal(jugador_objetivo.id, "H")
        if jugador_objetivo.check_puede_anular_el_intercambio():
            await juego.mensaje_personal(jugador_objetivo.id, "N")

        if not jugador_objetivo.get_efecto_seduccion():
            check_obstaculo(player_orig, jugador_objetivo.id, juego)

        return {"message": "se creo la solicitud de intercambio"}
    except HTTPException as e:
        error_msg = f"Error: {e.detail}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )


@router.post("/swap-response")
async def swap_response(match_id: int = Form(), card_id: int = Form(), player_orig: int = Form(), se_defiende: bool = Form()):
    try:
        juego = get_global_juego(match_id)
        jugador_orig = juego.get_jugador(player_orig)  # j4
        jugador_objetivo = juego.get_jugador_en_turno()  # j3
        check_carta_habilitada(card_id, jugador_orig, jugador_objetivo)
        '''si el jugador que glopea este endpoint (el objetivo del intercambio), pasa un card_id correspondiente a aterrador.
           significa que se niega al mismo. '''
        if is_card_defense(card_id) and se_defiende:
            await defenderse_de_intercambio(juego, card_id, jugador_orig, jugador_objetivo)
        else:
            if jugador_orig.get_cuartena() and jugador_objetivo.get_cuartena():
                await mostrar_cartas_cuarentena_ambos(jugador_orig, card_id, jugador_objetivo, juego.solicitud_intercambio.carta_solicitante, juego)
            else:
                await mostrar_cartas_cuarentena(jugador_orig, card_id, juego, 3)
                await mostrar_cartas_cuarentena(jugador_objetivo, juego.solicitud_intercambio.carta_solicitante, juego, 3)
            juego.responder_intercambio(player_orig, card_id)
        fallaste_card = is_fallaste(card_id) and se_defiende
        if not fallaste_card:
            juego.terminar_turno()
            juego.avanzar_turno()
        await juego.mensaje_personal(player_orig, "D")
        await juego.mensaje_personal(jugador_objetivo.id, "D")
        ganador = check_ganador(juego)
        if ganador:
            await juego.broadcast_global("K")
        if jugador_orig.get_efecto_seduccion():
            if fallaste_card:
                jugador_orig.remove_efecto_seduccion()
                proximo = juego.get_jugador_siguiente(jugador_orig)
                if proximo == jugador_objetivo:
                    proximo = juego.get_jugador_siguiente(proximo)
                proximo.set_efecto_seduccion()
            else:
                jugador = juego.get_jugador_en_turno()
                await juego.mensaje_personal(jugador.id, "E")
                jugador_orig.remove_efecto_seduccion()

        else:
            if not fallaste_card and not jugador_orig.get_efecto_fallaste():
                await juego.mensaje_personal(jugador_orig.id, "E")
            elif not fallaste_card and jugador_orig.get_efecto_fallaste():
                jugador_orig.remove_efecto_fallaste()
                jugador_turno = juego.get_jugador_en_turno()
                await juego.mensaje_personal(jugador_turno.id, "E")
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

######
# Decretar Finalizar Partida
######


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

######
# GET LOGS
######


@router.get("/log/{match_id}")
async def get_logs_del_juego(match_id: int):
    try:
        juego = get_global_juego(match_id)
        logs = juego.get_logs()
        return {
            "logs": logs,
        }
    except HTTPException as e:
        error_msg = f"Error: {e.detail}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

######
# Panico, Que quede entre nosotros.
######


@router.post("/play/que_quede_entre_nosotros")
async def que_quede_entre_nostros(match_id: int = Form(),
                                  player_objective: int = Form(),
                                  player_orig: int = Form()):
    try:
        juego = get_global_juego(match_id)
        jugador = get_jugador(player_orig, juego)
        check_turno(jugador)
        msg = play_que_quede_entre_nosotros(
            player_orig, player_objective, juego)
        await juego.mensaje_personal(player_objective, {"carta_id": 106,
                                                        "mensaje": msg["mensaje"],
                                                        "cartaMostrar": msg["cartaMostrar"]})
    except HTTPException as e:
        error_msg = f"Error:{e.detail}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    
@router.post("/play/cita_a_ciegas")
async def cita_a_ciegas(match_id: int = Form(),  card_id: int = Form(), player: int = Form()):
    try:
            juego   = get_global_juego(match_id)
            jugador = get_jugador(player, juego)
            check_turno(jugador)    
            msg = play_cita_a_ciegas(jugador,card_id, juego)
            await juego.mensaje_personal(player, "D")
            #tiene que ser global
            await juego.broadcast_global(   { "carta_id": 104, # ese indece corresponde a una carta, cita a iegas. 
                                              "mensaje": msg["mensaje"],
                                              "cartaMostrar":[]
                                            }
                                        )
            juego.agregar_log(msg["mensaje"])
            #se deberia avisar por un boadcast global que cambio el estado de la partida para quue se vea inmediatamente el nuevo log.
    except HTTPException as e:
        error_msg = "No se pudo, jugar cita a ciegas."


######
# Panico, Que quede entre nosotros.
######


@router.post("/play/vuelta_y_vuelta")
async def endpoint_vuelta_y_vuelta(match_id: int = Form(),
                                  card_id: int = Form(),
                                  player_orig: int = Form()):
    try:
        juego = get_global_juego(match_id)
        jugador = get_jugador(player_orig, juego)
        intercambio_vyv = juego.solicitud_intercambio_vyv
        if jugador == intercambio_vyv.primer_jugador:
            check_turno(jugador)
        jugador_proximo = juego.get_jugador_siguiente(jugador)
        check_carta_habilitada(card_id, jugador, jugador_proximo)
        if not intercambio_vyv.is_complete_vuelta_y_vuelta():
            intercambio_vyv.completar_vuelta_y_vuelta(jugador,card_id)
            proximo = juego.get_jugador_siguiente(jugador)
            if proximo != intercambio_vyv.primer_jugador:
                await juego.mensaje_personal(proximo.id,{"carta_especial": {
                                                        "tipo_carta": "Vuelta y vuelta",
                                                        "cartas": [],
                                                        "jugadores": []
                                                        }   
                                                    })
            mensaje = "El jugador " + jugador.name + " selecciono una carta correctamente." 
        if intercambio_vyv.is_complete_vuelta_y_vuelta():
            msg = play_vuelta_y_vuelta(player_orig,juego)
            await juego.broadcast_global("D")
            await juego.broadcast_global({"carta_id": 99,
                                          "mensaje": msg["mensaje"]})
            juego.terminar_turno()
            juego.avanzar_turno()
            jugador_proximo_turno = juego.get_jugador_en_turno()
            await juego.mensaje_personal(jugador_proximo_turno.id, "E")
            await juego.broadcast_global("C")
            mensaje = "Se completo el intercambio vuelta y vuelta correctamente"
        
        return {"resultado": mensaje}
    except HTTPException as e:
        error_msg = f"Error: {e.detail}"

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )






@router.post("/play/olvidadizo")
async def olvidadizo(match_id: int = Form(), card_id_elegida: int=Form(), player_id: int = Form()):
    try:
        juego = get_global_juego(match_id)
        jugador = juego.get_jugador(player_id)
        check_turno(jugador)
        msg = play_olvidadizo(juego, player_id, card_id_elegida)
        await juego.mensaje_personal(player_id, "D")
        return{"mensaje":"carta olvidadizo jugada"}
    except HTTPException as e:
        error_msg = f"Error: {e.detail}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

