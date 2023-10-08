from typing import List
from logic.game import Juego
from logic.player import JugadorPartida


def test_repartirCartas_4jugadoresCon4Cartas(mocker):    

    j1 = JugadorPartida(1)
    j2 = JugadorPartida(2)
    j3 = JugadorPartida(3)
    j4 = JugadorPartida(4)
    
    mazo : List[int] = {22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,1}

    juego                      = Juego(1,4,2,[1,2,3,4])
    juego.jugadores_en_partida = [j1,j2,j3,j4]
    juego.mazo                 = mazo 
    juego.repartir_cartas(4)

    for jugador in juego.jugadores_en_partida:
        assert len(jugador.cartas) == 4






