

from models.game import Juego
from utils.action_utils import get_jugador


def play_puerta_atrancada(juego: Juego, atacante_in: int, objetivo_in: int):
    
    # obtengo jugadores
    jugador_atacante = get_jugador(atacante_in, juego)
    jugador_objetivo = get_jugador(objetivo_in, juego)
    #valido vecinos
    juego.validar_posiciones_vecinas(
        atacante_in,
        objetivo_in)
    #obtengo posision intermedia
    indice_posicion_intermedia = juego.get_posicion_intermedia(objetivo_in, atacante_in)
    # aplico puerta atrancada
    juego.posiciones[indice_posicion_intermedia] = "p"
    
    msg = {
        "mensaje": jugador_atacante.name +
        " jugó carta Puerta atrancada contra " +
        jugador_objetivo.name}
    juego.agregar_log(msg["mensaje"])
    juego.agregar_log("Hay una puerta entre " + jugador_objetivo.name + " y " + jugador_atacante.name)
    return msg


def play_cuarentena(atacante_in: int, objetivo_in: int, juego: Juego):
    # obtengo jugadores
    jugador_atacante = juego.get_jugador(atacante_in)
    jugador_objetivo = juego.get_jugador(objetivo_in)
    #valido vecinos
    juego.validar_posiciones_vecinas(
        atacante_in,
        objetivo_in)
    # aplico cuarentena a objetivo
    jugador_objetivo.set_cuartena()

    msg = {
        "mensaje": jugador_atacante.name +
        " jugó carta Cuarentena contra " +
        jugador_objetivo.name}
    juego.agregar_log(msg["mensaje"])
    juego.agregar_log(jugador_objetivo.name + " esta en cuarentena gracias a " + jugador_atacante.name)
    return msg