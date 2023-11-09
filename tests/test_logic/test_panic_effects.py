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


@pytest.fixture
def mock_j2(mocker):
    mocker.patch("models.player.get_name", return_value="pedro")
    jugador = JugadorPartida(id=2)
    return jugador


def test_play_ups_ok(mock_juego, mock_j1):
    mock_juego.jugadores_en_partida = [mock_j1]
    mock_j1.cartas = [1, 2, 3, 4]
    msg = play_ups(mock_j1.id, mock_juego)
    assert (msg["mensaje"] == "pepe jugó la carta ¡Ups!")
    assert (msg["cartaMostrar"] == [
        {'id': 1}, {'id': 2}, {'id': 3}, {'id': 4}])


def test_play_tres_cuatro_ok(mock_juego, mock_j1):
    mock_juego.jugadores_en_partida = [mock_j1]
    mock_juego.posiciones = [1, "p", 2, 0, 3, "p", 4, "p"]
    msg = play_tres_cuatro(mock_j1.id, mock_juego)
    assert (msg["mensaje"] == "pepe jugó la carta Tres,Cuatro...")
    assert (mock_juego.posiciones == [1, 0, 2, 0, 3, 0, 4, 0])


def test_play_cuerdas_podridas_ok(mock_juego, mock_j1):
    mock_j1.cuarentena = (True, 2)
    mock_juego.jugadores_en_partida = [mock_j1, mock_j1, mock_j1]
    for jugador in mock_juego.jugadores_en_partida:
        assert (jugador.get_cuartena() == True)
    msg = play_cuerdas_podridas(mock_j1.id, mock_juego)
    assert (msg["mensaje"] == "pepe jugó la carta Cuerdas Podridas.")
    for jugador in mock_juego.jugadores_en_partida:
        assert (jugador.get_cuartena() == False)


def test_play_es_aqui_la_fiesta_ok_pares(mock_juego, mock_j1):
    mock_juego.posiciones = [1, 0, 2, 0, 3, 0, 4, 0]
    mock_id_inicio = 3
    msg = play_es_aqui_la_fiesta(mock_id_inicio, mock_juego)
    assert (msg["mensaje"] == "pepe jugó la carta Es Aqui la Fiesta?.")
    assert mock_juego.posiciones == [4, 0, 3, 0, 2, 0, 1, 0]


def test_play_es_aqui_la_fiesta_ok_impares(mock_juego, mock_j1):
    mock_juego.posiciones = [1, 0, 2, 0, 3, 0, 4, 0, 5, 0]
    mock_id_inicio = 3
    msg = play_es_aqui_la_fiesta(mock_id_inicio, mock_juego)
    assert (msg["mensaje"] == "pepe jugó la carta Es Aqui la Fiesta?.")
    assert mock_juego.posiciones == [5, 0, 3, 0, 2, 0, 4, 0, 1, 0]


def test_play_que_qude_entre_nosotros_ok(mocker, mock_juego, mock_j1, mock_j2):
    mock_juego.jugadores_en_partida = [mock_j1, mock_j2]
    mock_j1.cartas = [1, 2, 3, 4]
    msg = play_que_quede_entre_nosotros(
        mock_j1.id, mock_j2.id, mock_juego)
    assert (msg["mensaje"] == "pepe jugó la carta Que quede entre nosotros...")
    assert (msg["cartaMostrar"] == [
        {'id': 1}, {'id': 2}, {'id': 3}, {'id': 4}])
