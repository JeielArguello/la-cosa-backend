from fastapi.testclient import TestClient
from unittest.mock import Mock

import pytest
from models.game import Juego
from logic.defense_effects import *


from main import app
from models.player import JugadorPartida

client = TestClient(app)

mocker = Mock()



@pytest.fixture
def mock_atacante(mocker):
    mocker.patch("models.player.get_name", return_value="pepe")
    jugador = JugadorPartida(id=1)
    jugador.cartas=[3,70,75,80]
    return jugador


@pytest.fixture
def mock_objetivo(mocker):
    mocker.patch("models.player.get_name", return_value="pedro")
    jugador = JugadorPartida(id=2)
    jugador.cartas=[5,6,7,8]
    return jugador


@pytest.fixture
def mock_juego(mocker):
    mocker.patch("models.player.get_name", return_value="pepe")
    juego = Juego(partida_id=1, cantidad_jugadores=4,
                  creador=1, jugadores_id=[1, 3, 2, 4])
    juego.name = "test"
    juego.posiciones = [1, 0, 2, 0, 3, 0, 4, 0]
    return juego

@pytest.fixture
def mock_card_id(mocker):
    card_id = 75
    return card_id


def test_defensa_no_gracias_succes(mock_juego, mock_atacante, mock_objetivo, mock_card_id):
    mock_intercambio = IntercambiarCarta(mock_objetivo, mock_card_id,mock_atacante)
    mock_juego.solicitud_intercambio = mock_intercambio
    mock_juego.jugadores_en_partida = [mock_atacante, mock_objetivo]
    msg = defensa_no_gracias(mock_juego, mock_atacante, mock_objetivo, mock_card_id)
    assert msg == {"mensaje": "pepe jugó carta no gracias contra pedro"}


def test_defensa_no_gracias_fail(mock_juego, mock_atacante, mock_objetivo, mock_card_id):
    mock_intercambio = None
    mock_juego.solicitud_intercambio = mock_intercambio
    mock_juego.jugadores_en_partida = [mock_atacante, mock_objetivo]
    mock_juego.solicitud_intercambio = mock_intercambio
    with pytest.raises(HTTPException) as exc:
        defensa_no_gracias(mock_juego, mock_atacante, mock_objetivo, mock_card_id)
    assert exc.value.status_code == 400
    assert exc.value.detail == "No hay solicitud de intercambio."


def test_defensa_aterrador(mock_juego, mock_atacante, mock_objetivo, mock_card_id):
    mock_intercambio = IntercambiarCarta(mock_objetivo, 5,mock_atacante)
    mock_juego.solicitud_intercambio = mock_intercambio
    mock_juego.jugadores_en_partida = [mock_atacante, mock_objetivo]
    msg = defense_aterrador(mock_juego, mock_atacante, mock_objetivo, mock_card_id)
    assert (msg["mensaje"] == "pepe jugó carta aterrador contra pedro")
    assert(msg["cartaMostrar"]==[{"id":5}])


def test_defensa_aterrador_fail(mock_juego, mock_atacante, mock_objetivo, mock_card_id):
    mock_intercambio = None
    mock_juego.solicitud_intercambio = mock_intercambio
    mock_juego.jugadores_en_partida = [mock_atacante, mock_objetivo]
    mock_juego.solicitud_intercambio = mock_intercambio
    with pytest.raises(HTTPException) as exc:
        defense_aterrador(mock_juego, mock_atacante, mock_objetivo, mock_card_id)
    assert exc.value.status_code == 400
    assert exc.value.detail == "No hay solicitud de intercambio"