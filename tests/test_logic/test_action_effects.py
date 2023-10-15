from fastapi.testclient import TestClient
from unittest.mock import Mock

import pytest
from models.game import Juego
from logic.action_effects import *


from main import app

client = TestClient(app)

mocker = Mock()

@pytest.fixture
def mock_juego():
    juego = Juego(partida_id=1, cantidad_jugadores=4,
                 creador=1, jugadores_id=[1, 3, 2, 4])
    juego.posiciones = [1, 0, 2, 0, 3, 0, 4, 0]
    return juego

def test_lanzallamas_simple(mocker):
    mock_atacante = 1
    mock_objetivo = 2
    mock_juego = Juego(partida_id=1, cantidad_jugadores=2,
                       creador=1, jugadores_id=[1, 2])
    play_lanzallamas(mock_atacante, mock_objetivo, mock_juego)
    response = {'jugadores': len(mock_juego.jugadores_en_partida),
                'posiciones': mock_juego.posiciones}
    assert response == {'jugadores': 2, 'posiciones': [1, 0]}


def test_lanzallamas(mocker):
    mock_juego = Juego(partida_id=1, cantidad_jugadores=10,
                       creador=1, jugadores_id=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    play_lanzallamas(4, 5, mock_juego)
    response1 = {'jugadores': len(mock_juego.jugadores_en_partida),
                 'posiciones': mock_juego.posiciones}
    assert response1 == {
        'jugadores': 10,
        'posiciones': [
            1,
            0,
            2,
            0,
            3,
            0,
            4,
            0,
            6,
            0,
            7,
            0,
            8,
            0,
            9,
            0,
            10,
            0]}
    play_lanzallamas(9, 8, mock_juego)
    response2 = {'jugadores': len(mock_juego.jugadores_en_partida),
                 'posiciones': mock_juego.posiciones}

    assert response2 == {'jugadores': 10, 'posiciones': [
        1, 0, 2, 0, 3, 0, 4, 0, 6, 0, 7, 0, 9, 0, 10, 0]}
    play_lanzallamas(10, 1, mock_juego)
    response3 = {'jugadores': len(mock_juego.jugadores_en_partida),
                 'posiciones': mock_juego.posiciones}
    assert response3 == {
        'jugadores': 10, 'posiciones': [
            2, 0, 3, 0, 4, 0, 6, 0, 7, 0, 9, 0, 10, 0]}
    play_lanzallamas(2, 10, mock_juego)
    response4 = {'jugadores': len(mock_juego.jugadores_en_partida),
                 'posiciones': mock_juego.posiciones}
    assert response4 == {'jugadores': 10,
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


def test_mas_vale_que_corras_succes(mock_juego):
    mock_atacante = 1
    mock_objetivo = 2
    play_mas_vale_que_corras(mock_atacante, mock_objetivo, mock_juego)
    response = {'jugadores': len(mock_juego.jugadores_en_partida),
                'posiciones': mock_juego.posiciones}
    assert response == {'jugadores': 4, 'posiciones': [2, 0, 1, 0, 3, 0, 4, 0]}