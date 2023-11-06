from fastapi import HTTPException
from models.game import Juego, robar_carta
from models.player import JugadorPartida
from models.swap_card import IntercambiarCarta


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
        " jugó carta aterrador contra " +
        jObj.name, 
        "cartaMostrar":[{"id": intercambio.carta_solicitante}]}
    del intercambio
    juego.agregar_log(msg["mensaje"])
    juego.agregar_log(jOrig.name + " cancelo intercambio con " + jObj.name )
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
        " jugó carta no gracias contra "+
        jugador_atacante.name
    }
    juego.agregar_log(["mensaje"])
    juego.agregar_log(jugador_no_gracias.name + " canceló intercambio con "+ jugador_atacante.name)
    return msg