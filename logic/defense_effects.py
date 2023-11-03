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
    del intercambio

