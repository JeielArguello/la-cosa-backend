from fastapi.testclient import TestClient
from unittest.mock import Mock

import pytest
from models.game import Juego
from logic.panic_effects import *


from main import app
from models.player import JugadorPartida

client = TestClient(app)

mocker = Mock()


@pytest.fixture
def mock_juego(mocker):
    mocker.patch("models.player.get_name", return_value="pepe")
    juego = Juego(partida_id=1, cantidad_jugadores=4,
                  creador=1, jugadores_id=[1, 3, 2, 4])
    juego.name = "test"
    juego.posiciones = [1, 0, 2, 0, 3, 0, 4, 0]
    return juego


@pytest.fixture
def mock_j1(mocker):
    mocker.patch("models.player.get_name", return_value="pepe")
    jugador = JugadorPartida(id=1)
    return jugador


def test_play_ups_succes(mocker, mock_juego, mock_j1):
    mock_juego.jugadores_en_partida = [mock_j1]
    mock_j1.cartas = [1, 2, 3, 4]
    mock_card_id = 105
    msg = play_ups(mock_j1.id, mock_juego, mock_card_id)
    assert(msg["mensaje"] == "pepe jugó la carta Ups.")
    assert(msg["cartaMostrar"] == [
           {'id': 1}, {'id': 2}, {'id': 3}, {'id': 4}])


def test_play_tres_cuatro(mocker, mock_juego, mock_j1):
    mock_juego.jugadores_en_partida = [mock_j1]
    mock_juego.posiciones = [1, "p", 2, 0, 3, "p", 4, "p"]
    mock_card_id = 93
    msg = play_tres_cuatro(mock_j1.id, mock_juego, mock_card_id)
    assert(msg["mensaje"] == "pepe jugó la carta Tres,Cuatro...")
    assert(mock_juego.posiciones == [1, 0, 2, 0, 3, 0, 4, 0])
