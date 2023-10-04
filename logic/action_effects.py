from logic.game import Juego


def play_lanzallamas(atacante_in: int, objetivo_in: int, juego: Juego):
    # get Jugador objetivo
    for jugador in juego.jugadores_en_partida:
        if jugador.id == objetivo_in:
            objetivo = jugador
    # get indices
    indice_objetivo = juego.posiciones.index(objetivo_in)
    indice_atacante = juego.posiciones.index(atacante_in)
    indice_posicion_intermedia = get_posicion_intermedia(
        juego.posiciones, indice_objetivo, indice_atacante)
    # check obstaculos
    if juego.posiciones[indice_posicion_intermedia] != 0:
        pass
    # check defensa
    # elif defensa:
    #     pass
    # eliminar jugador y posiciones
    else:
        juego.jugadores_en_partida.remove(objetivo)
        del juego.posiciones[max(indice_objetivo, indice_posicion_intermedia)]
        del juego.posiciones[min(indice_objetivo, indice_posicion_intermedia)]


def get_posicion_intermedia(posiciones, indice_jugador1, indice_jugador2):
    border_one = (indice_jugador1 == 0 and indice_jugador2 ==
                  len(posiciones) - 1)
    border_two = (indice_jugador2 == 0 and indice_jugador1 ==
                  len(posiciones) - 1)
    if (border_one or border_two):
        posicion = len(posiciones) - 1
    else:
        posicion = min(indice_jugador1, indice_jugador2) + 1
    return posicion
