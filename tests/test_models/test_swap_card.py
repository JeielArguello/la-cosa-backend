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
    mocker.patch("models.player.get_id_avatar", return_value=1)
    jugador = JugadorPartida(id=1)
    return jugador


@pytest.fixture
def mock_j2(mocker):
    mocker.patch("models.player.get_name", return_value="pedro")
    mocker.patch("models.player.get_id_avatar", return_value=1)
    jugador = JugadorPartida(id=2)
    return jugador

@pytest.fixture
def mock_intercambio(mock_j1, mock_j2):
    swap_card = IntercambiarCarta(mock_j1, 1, mock_j2)    
    return swap_card


def test_sawp_check_receptor_ok(mock_j1, mock_j2):
    player_orig = mock_j1
    player_objetive = mock_j2
    swap_card = IntercambiarCarta(player_orig, 1, player_objetive)
    swap_card.check_receptor(2)


def test_swap_check_receptor_http_exception_no_eres_receptor(mock_intercambio,mock_j1, mock_j2):
    player_orig = mock_j1
    player_objetive = mock_j2
    swap_card = IntercambiarCarta(player_orig, 1, player_objetive)
    try:
        swap_card.check_receptor(3)
    except HTTPException as e:
        assert e.status_code == 400
        assert e.detail == "No eres el receptor del intercambio"



def test_swap_completar_intercambio_ok(mock_intercambio, mock_j1, mock_j2):
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



def test_completar_intercambio_y_objetivo_infectado_ok(mock_intercambio, mock_j1, mock_j2):
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

def test_completar_intercambio_y_origen_infectado_ok(mock_intercambio, mock_j1, mock_j2):
    player_orig = mock_j1
    player_objetive = mock_j2
    player_objetive.agregar_carta(2)
    player_orig.agregar_carta(23)
    player_objetive.set_la_cosa()
    swap_card: IntercambiarCarta = mock_intercambio
    swap_card.carta_solicitante = 23
    swap_card.completar_intercambio(2)
    assert swap_card.carta_receptor == 2
    assert player_orig.get_cartas() == [{'id': 2}]
    assert player_objetive.get_cartas() == [{'id': 23}]
    assert player_objetive.get_la_cosa()
    assert player_orig.get_infectado()
