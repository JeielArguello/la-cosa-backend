from unittest.mock import Mock
import pytest
from models.swap_card import IntercambiarCarta
from models.player import JugadorPartida
from fastapi import HTTPException
from fastapi.testclient import TestClient


from main import app
client = TestClient(app)

mocker = Mock()


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

@pytest.fixture
def mock_intercambio(mock_j1, mock_j2):
    swap_card = IntercambiarCarta(mock_j1, 1, mock_j2)    
    return swap_card



def test_check_receptor_success( mock_intercambio):
    mock_intercambio.check_receptor(2)


def test_check_receptor_fail(mock_intercambio):
    swap_card = mock_intercambio
    try:
        swap_card.check_receptor(3)
    except HTTPException as e:
        assert e.status_code == 400
        assert e.detail == "No eres el receptor del intercambio"


def test_completar_intercambio_success(mock_j1, mock_j2, mock_intercambio):
    player_orig = mock_j1
    player_objetive = mock_j2
    player_orig.agregar_carta(22)
    player_objetive.agregar_carta(23)
    swap_card: IntercambiarCarta = mock_intercambio
    swap_card.carta_solicitante = 22
    swap_card.completar_intercambio(23)
    assert swap_card.carta_receptor == 23
    assert player_orig.get_cartas() == [{'id': 23}]
    assert player_objetive.get_cartas() == [{'id': 22}]


def test_completar_intercambio_infectado(mock_j1, mock_j2, mock_intercambio):
    player_orig = mock_j1
    player_objetive = mock_j2
    player_orig.agregar_carta(2)
    player_objetive.agregar_carta(23)
    player_orig.set_la_cosa()
    swap_card: IntercambiarCarta = mock_intercambio
    swap_card.carta_solicitante = 2
    swap_card.completar_intercambio(23)
    assert swap_card.carta_receptor == 23
    assert player_orig.get_cartas() == [{'id': 23}]
    assert player_objetive.get_cartas() == [{'id': 2}]
    assert player_orig.get_la_cosa()
    assert player_objetive.get_infectado()
