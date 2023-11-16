from fastapi.testclient import TestClient
from unittest.mock import Mock

import pytest
from logic.obstacle_effects import play_cuarentena, play_puerta_atrancada
from models.game import Juego
from logic.action_effects import *


from main import app
from models.player import JugadorPartida

client = TestClient(app)

mocker = Mock()


@pytest.fixture
def mock_juego(mocker):
    mocker.patch("models.player.get_name", return_value="pepe")
    mocker.patch("models.player.get_id_avatar", return_value=1)
    juego = Juego(partida_id=1, cantidad_jugadores=4,
                  creador=1, jugadores_id=[1, 3, 2, 4])
    juego.name = "test"
    juego.posiciones = [1, 0, 2, 0, 3, 0, 4, 0]
    return juego


@pytest.fixture
def mock_atacante(mocker):
    mocker.patch("models.player.get_name", return_value="pepe")
    mocker.patch("models.player.get_id_avatar", return_value=1)
    jugador = JugadorPartida(id=1)
    return jugador


@pytest.fixture
def mock_objetivo(mocker):
    mocker.patch("models.player.get_name", return_value="pedro")
    mocker.patch("models.player.get_id_avatar", return_value=1)
    jugador = JugadorPartida(id=4)
    return jugador


@pytest.fixture
def mock_objetivo_no_vecino(mocker):
    mocker.patch("models.player.get_name", return_value="jasinto")
    mocker.patch("models.player.get_id_avatar", return_value=1)
    jugador = JugadorPartida(id=3)
    return jugador

# Test 1: puerta atrancada aplicada correctamente


def test_play_puerta_atrancada_ok(mocker, mock_juego, mock_atacante, mock_objetivo):
    juego = mock_juego
    mocker.patch("logic.obstacle_effects.get_jugador",
                 side_effect={mock_atacante, mock_objetivo})
    expected_posiciones = [1, 0, 2, 0, 3, 0, 4, "p"]
    expected_msg = {
        "mensaje": "pepe jugó carta Puerta atrancada contra pedro"
    }
    expected_msg_2 = {
        "mensaje": "pedro jugó carta Puerta atrancada contra pepe"
    }
    msg = play_puerta_atrancada(juego, mock_atacante.id, mock_objetivo.id)
    assert msg == expected_msg or msg == expected_msg_2
    assert juego.posiciones == expected_posiciones

# Test 2: puerta atrancada falla por no ser vecinos


def test_play_puerta_atrancada__http_exception_no_vecino(mocker, mock_juego, mock_atacante, mock_objetivo_no_vecino):
    juego = mock_juego
    mocker.patch("logic.obstacle_effects.get_jugador", side_effect={
                 mock_atacante, mock_objetivo_no_vecino})
    mocker.patch("logic.obstacle_effects.Juego.validar_posiciones_vecinas",
                 side_effect=HTTPException(status_code=400, detail="Los jugadores no son vecinos"))
    with pytest.raises(HTTPException) as excinfo:
        play_puerta_atrancada(juego, mock_atacante.id,
                              mock_objetivo_no_vecino.id)
    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Los jugadores no son vecinos"

# Test 1: cuarentena aplicada correctamente
def test_play_cuarentena_succes(mocker, mock_juego,mock_atacante, mock_objetivo):
    juego:Juego = mock_juego
    jugador_objetivo: JugadorPartida = mock_objetivo
    jugador_atacanate: JugadorPartida = mock_atacante
    mocker.patch("logic.obstacle_effects.Juego.get_jugador", side_effect=[jugador_atacanate, jugador_objetivo])
    expected_msg = {
        "mensaje": "pepe jugó carta Cuarentena contra pedro"
    }
    msg = play_cuarentena(mock_atacante.id, mock_objetivo.id, juego)
    assert msg == expected_msg 
    assert jugador_objetivo.get_cuartena() == True 
    assert juego.get_logs()[-1] == "pedro esta en cuarentena gracias a pepe"

# Test 2: cuarentena falla por no ser vecinos
def test_play_cuarentena_no_vecino(mocker, mock_juego,mock_atacante, mock_objetivo_no_vecino):
    juego = mock_juego
    mocker.patch("logic.obstacle_effects.get_jugador", side_effect=[mock_atacante, mock_objetivo_no_vecino]) 
    with pytest.raises(HTTPException) as excinfo:
        play_cuarentena(mock_atacante.id, mock_objetivo_no_vecino.id, juego)
    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Los jugadores no son vecinos"

