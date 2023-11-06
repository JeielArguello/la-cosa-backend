

from models.game import Juego
from utils.action_utils import get_jugador, get_posicion_intermedia, validar_posiciones_vecinas


def play_puerta_atrancada(juego: Juego, atacante_in: int, objetivo_in: int):
    
    # obtengo jugadores
    jugador_atacante = get_jugador(atacante_in, juego)
    jugador_objetivo = get_jugador(objetivo_in, juego)
    # obtengo el indice de los jugadores
    indice_objetivo = juego.posiciones.index(objetivo_in)
    indice_atacante = juego.posiciones.index(atacante_in)
    #valido vecinos
    len_posiciones = len(juego.posiciones)
    validar_posiciones_vecinas(
        indice_atacante,
        indice_objetivo,
        len_posiciones)
    #obtengo posision intermedia
    indice_posicion_intermedia = get_posicion_intermedia(
        len_posiciones, indice_objetivo, indice_atacante)
    # aplico puerta atrancada
    juego.posiciones[indice_posicion_intermedia] = "p"
    
    msg = {
        "mensaje": jugador_atacante.name +
        " jugó carta puerta atrancada contra " +
        jugador_objetivo.name}
    return msg