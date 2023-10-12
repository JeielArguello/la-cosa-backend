from fastapi.testclient import TestClient
from unittest.mock import Mock
from models.game import Juego, robar_carta
from models.player import JugadorPartida
from fastapi import HTTPException


from main import app

client = TestClient(app)

mocker = Mock()


# def test_robar_carta(mocker):
#     mock_carta_1 = 1
#     mock_carta_2 = 2
#     mock_juego = Juego(partida_id=1, cantidad_jugadores=2,
#                        creador=1, jugadores_id=[1, 2])
#     mock_juego.mazo.append(mock_carta_1)
#     mock_juego.mazo.append(mock_carta_2)

#     robar_carta(mock_juego, mock_juego.jugadores_en_partida[0])
#     robar_carta(mock_juego, mock_juego.jugadores_en_partida[0])
#     try:
#         robar_carta(mock_juego, mock_juego.jugadores_en_partida[0])
#     except HTTPException as e:
#         error_msg = {e.detail}
#     jugador = mock_juego.jugadores_en_partida[0]
#     cartas = jugador.cartas
#     response = {'mano_jugador': cartas}
#     assert response == {'mano_jugador': [mock_carta_2, mock_carta_1]}
#     assert error_msg == {"El mazo esta vacio"}
