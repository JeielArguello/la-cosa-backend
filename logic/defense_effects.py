from fastapi import HTTPException
from models.game import Juego
from models.player import JugadorPartida
from models.swap_card import IntercambiarCarta
from models.constants import *



def defense_aterrador(juego: Juego,jOrig: JugadorPartida,jObj:JugadorPartida, card_id:int):
    intercambio:IntercambiarCarta = juego.solicitud_intercambio
    if intercambio is None:
        raise HTTPException(
            status_code=400,
            detail="No hay solicitud de intercambio")
    
    jOrig.descartar_carta(card_id)
    juego.robar_carta_no_panico(jOrig)
    juego.solicitud_intercambio = None    
    msg = {
        "mensaje": jOrig.name +
        " jugó carta Aterrador contra " +
        jObj.name, 
        "cartaMostrar":[{"id": intercambio.carta_solicitante}]}
    del intercambio
    juego.agregar_log(msg["mensaje"])
    juego.agregar_log(jOrig.name + " miro la carta de " + jObj.name +" y cancelo el intercambio")
    return msg


def defensa_no_gracias(juego: Juego, jugador_no_gracias: JugadorPartida,
                        jugador_atacante: JugadorPartida, card_id:int):
    intercambio:IntercambiarCarta = juego.solicitud_intercambio
    if intercambio is None:
        raise HTTPException(
            status_code = 400,
            detail = "No hay solicitud de intercambio."
        ) 
    jugador_no_gracias.descartar_carta(card_id)
    juego.robar_carta_no_panico(jugador_no_gracias)
    juego.solicitud_intercambio = None
    msg = {
        "mensaje": jugador_no_gracias.name +
        " jugó carta ¡No, gracias! contra "+
        jugador_atacante.name
    }
    juego.agregar_log(msg["mensaje"])
    juego.agregar_log(jugador_no_gracias.name + " canceló intercambio con "+ jugador_atacante.name)
    return msg


async def defensa_fallaste(juego: Juego, jugador_defensor: JugadorPartida,
                        jugador_atacante: JugadorPartida, card_id:int):
    intercambio:IntercambiarCarta = juego.solicitud_intercambio
    if intercambio is None:
        raise HTTPException(
            status_code = 400,
            detail = "No hay solicitud de intercambio."
        ) 
    jugador_defensor.descartar_carta(card_id)
    juego.robar_carta_no_panico(jugador_defensor)
    
    jugador_siguiente_defensor = juego.get_jugador_siguiente(jugador_defensor)

    if jugador_siguiente_defensor == jugador_atacante:
        jugador_siguiente_defensor = juego.get_jugador_siguiente(jugador_siguiente_defensor)
    if not juego.is_obstaculo(jugador_defensor.id, jugador_siguiente_defensor.id) and not jugador_siguiente_defensor.get_cuartena():
        paso_intercambio = True
        intercambio.cambiar_receptor(jugador_siguiente_defensor)
        jugador_siguiente_defensor.set_efecto_fallaste()
        await juego.mensaje_personal(jugador_siguiente_defensor.id,HABILITADO_R_INTERCAMBIO)
        if jugador_siguiente_defensor.check_puede_anular_el_intercambio():
            await juego.mensaje_personal(jugador_siguiente_defensor.id,HABILITADO_D_INTERCAMBIO)
    else:
        paso_intercambio = False
        juego.solicitud_intercambio = None
        del intercambio 
        juego.terminar_turno()
        juego.avanzar_turno()
        jugador_en_turno = juego.get_jugador_en_turno()
        await juego.mensaje_personal(jugador_en_turno.id,HABILITADO_ROBAR_CARTA)
    
    msg = {
        "mensaje": jugador_defensor.name +
        " jugó carta ¡Fallaste! contra "+
        jugador_atacante.name 
    }
    juego.agregar_log(msg["mensaje"])
    if paso_intercambio:
        juego.agregar_log(jugador_defensor.name + " canceló intercambio con "+ jugador_atacante.name
                          + " y le paso el intercambio a " + jugador_siguiente_defensor.name)
    else:
        juego.agregar_log(jugador_defensor.name + " canceló intercambio con "+ jugador_atacante.name)
    return msg


def defensa_nada_de_barbacoas(juego: Juego, jugador_defensor: JugadorPartida,
                        jugador_atacante: JugadorPartida, card_id: int):
    jugador_defensor.descartar_carta(card_id)
    juego.robar_carta_no_panico(jugador_defensor)
    msg = {
        "mensaje": jugador_atacante.name +
        " jugó Lanzallama contra " +
        jugador_defensor.name +
        ", pero se defendió con ¡Nada de barbacoas!"}
    juego.agregar_log(msg["mensaje"])
    return msg

def defensa_aqui_estoy_bien(juego: Juego, jugador_defensor: JugadorPartida,
                        jugador_atacante: JugadorPartida, card_id: int, nombre_ataque:str):
    
    jugador_defensor.descartar_carta(card_id)
    juego.robar_carta_no_panico(jugador_defensor)
    msg = {
        "mensaje": jugador_atacante.name +
        " jugó "+nombre_ataque+" contra " +
        jugador_defensor.name +
        ", pero se defendió con Aquí estoy bien"}
    juego.agregar_log(msg["mensaje"])
    return msg