from fastapi.testclient import TestClient
from unittest.mock import Mock
from logic.game import Juego
from logic.action_effects import *


from main import app

client = TestClient(app)

mocker = Mock()


def test_lanzallamas_simple(mocker):
    mock_atacante = 1
    mock_objetivo = 2
    mock_juego = Juego(partida_id=1, cantidad_jugadores=2,
                       creador=1, jugadores_id=[1, 2])
    play_lanzallamas(mock_atacante, mock_objetivo, mock_juego)
    response = {'jugadores': len(mock_juego.jugadores_en_partida),
                'posiciones': mock_juego.posiciones}
    assert response == {'jugadores': 1, 'posiciones': [1, 0]}


def test_lanzallamas(mocker):
    mock_juego = Juego(partida_id=1, cantidad_jugadores=10,
                       creador=1, jugadores_id=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    play_lanzallamas(4, 5, mock_juego)
    response1 = {'jugadores': len(mock_juego.jugadores_en_partida),
                 'posiciones': mock_juego.posiciones}
    assert response1 == {'jugadores': 9,
                         'posiciones': [1, 0, 2, 0, 3, 0, 4, 0, 6, 0, 7, 0, 8, 0, 9, 0, 10, 0]}
    play_lanzallamas(9, 8, mock_juego)
    response2 = {'jugadores': len(mock_juego.jugadores_en_partida),
                 'posiciones': mock_juego.posiciones}

    assert response2 == {'jugadores': 8,
                         'posiciones': [1, 0, 2, 0, 3, 0, 4, 0, 6, 0, 7, 0, 9, 0, 10, 0]}
    play_lanzallamas(10, 1, mock_juego)
    response3 = {'jugadores': len(mock_juego.jugadores_en_partida),
                 'posiciones': mock_juego.posiciones}
    assert response3 == {'jugadores': 7,
                         'posiciones': [2, 0, 3, 0, 4, 0, 6, 0, 7, 0, 9, 0, 10, 0]}
    play_lanzallamas(2, 10, mock_juego)
    response4 = {'jugadores': len(mock_juego.jugadores_en_partida),
                 'posiciones': mock_juego.posiciones}
    assert response4 == {'jugadores': 6,
                         'posiciones': [2, 0, 3, 0, 4, 0, 6, 0, 7, 0, 9, 0]}


def test_lanzallamas_no_vecinos(mocker):
    mock_atacante = 1
    mock_objetivo = 2
    mock_juego = Juego(partida_id=1, cantidad_jugadores=4,
                       creador=1, jugadores_id=[1, 3, 2, 4])
    try:
        play_lanzallamas(mock_atacante, mock_objetivo, mock_juego)
    except HTTPException as e:
        error_msg = {e.detail}
    assert error_msg == {"Los jugadores no son vecinos"}
