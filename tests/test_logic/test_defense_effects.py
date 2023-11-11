from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, Mock

import pytest
from models.game import Juego
from logic.defense_effects import *


from main import app
from models.player import JugadorPartida

client = TestClient(app)

mocker = Mock()

mocker2 = AsyncMock()


@pytest.fixture
def mock_atacante(mocker):
    mocker.patch("models.player.get_name", return_value="pepe")
    mocker.patch("models.player.get_id_avatar", return_value=1)
    jugador = JugadorPartida(id=1)
    jugador.cartas = [3, 70, 75, 80]
    return jugador


@pytest.fixture
def mock_objetivo(mocker):
    mocker.patch("models.player.get_name", return_value="pedro")
    mocker.patch("models.player.get_id_avatar", return_value=1)
    jugador = JugadorPartida(id=2)
    jugador.cartas = [5, 6, 77, 78]
    return jugador


@pytest.fixture
def mock_proximo(mocker):
    mocker.patch("models.player.get_name", return_value="pedro")
    mocker.patch("models.player.get_id_avatar", return_value=1)
    jugador = JugadorPartida(id=3)
    jugador.cartas = [53, 61, 7, 71]
    return jugador


@pytest.fixture
def mock_proximo2(mocker):
    mocker.patch("models.player.get_name", return_value="pedro")
    mocker.patch("models.player.get_id_avatar", return_value=1)
    jugador = JugadorPartida(id=4)
    jugador.cartas = [53, 61, 7, 71]
    return jugador


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
def mock_juego_async(mocker):
    mocker.patch("models.player.get_name", return_value="pepe")
    mocker.patch("models.player.get_id_avatar", return_value=1)
    juego = Juego(partida_id=1, cantidad_jugadores=4,
                  creador=1, jugadores_id=[1, 3, 2, 4])
    juego.name = "test"
    juego.posiciones = [1, 0, 2, 0, 3, 0, 4, 0]
    return juego


@pytest.fixture
def mock_card_id():
    card_id = 75
    return card_id


def test_defensa_no_gracias_ok(mock_juego, mock_atacante, mock_objetivo, mock_card_id):
    mock_intercambio = IntercambiarCarta(
        mock_objetivo, mock_card_id, mock_atacante)
    mock_juego.solicitud_intercambio = mock_intercambio
    mock_juego.jugadores_en_partida = [mock_atacante, mock_objetivo]
    msg = defensa_no_gracias(mock_juego, mock_atacante,
                             mock_objetivo, mock_card_id)
    assert msg == {"mensaje": "pepe jugó carta ¡No, gracias! contra pedro"}


def test_defensa_no_gracias_http_exception_no_hay_solicitud_intercambio(mock_juego, mock_atacante, mock_objetivo, mock_card_id):
    mock_intercambio = None
    mock_juego.solicitud_intercambio = mock_intercambio
    mock_juego.jugadores_en_partida = [mock_atacante, mock_objetivo]
    mock_juego.solicitud_intercambio = mock_intercambio
    with pytest.raises(HTTPException) as exc:
        defensa_no_gracias(mock_juego, mock_atacante,
                           mock_objetivo, mock_card_id)
    assert exc.value.status_code == 400
    assert exc.value.detail == "No hay solicitud de intercambio."


def test_defensa_aterrador_ok(mock_juego, mock_atacante, mock_objetivo, mock_card_id):
    mock_intercambio = IntercambiarCarta(mock_objetivo, 5, mock_atacante)
    mock_juego.solicitud_intercambio = mock_intercambio
    mock_juego.jugadores_en_partida = [mock_atacante, mock_objetivo]
    msg = defense_aterrador(mock_juego, mock_atacante,
                            mock_objetivo, mock_card_id)
    assert (msg["mensaje"] == "pepe jugó carta Aterrador contra pedro")
    assert (msg["cartaMostrar"] == [{"id": 5}])


def test_defensa_aterrador_http_exception_no_hay_solicitud_intercambio(mock_juego, mock_atacante, mock_objetivo, mock_card_id):
    mock_intercambio = None
    mock_juego.solicitud_intercambio = mock_intercambio
    mock_juego.jugadores_en_partida = [mock_atacante, mock_objetivo]
    mock_juego.solicitud_intercambio = mock_intercambio
    with pytest.raises(HTTPException) as exc:
        defense_aterrador(mock_juego, mock_atacante,
                          mock_objetivo, mock_card_id)
    assert exc.value.status_code == 400
    assert exc.value.detail == "No hay solicitud de intercambio"


@pytest.mark.asyncio
async def test_defensa_fallaste_ok(mocker, mock_juego_async, mock_atacante, mock_objetivo, mock_card_id, mock_proximo, mock_proximo2):
    mock_intercambio = IntercambiarCarta(
        mock_objetivo, mock_card_id, mock_atacante)
    mock_juego_async.solicitud_intercambio = mock_intercambio
    mock_juego_async.jugadores_en_partida = [
        mock_atacante, mock_objetivo, mock_proximo, mock_proximo2]
    mock_card_id = 78
    mock_objetivo.cartas = [5, 6, 78, 8]
    mocker.patch("logic.defense_effects.Juego.mensaje_personal",
                 return_value=None)
    msg = await defensa_fallaste(mock_juego_async, mock_objetivo, mock_atacante, mock_card_id)
    assert msg == {"mensaje": "pedro jugó carta ¡Fallaste! contra pepe"}


@pytest.mark.asyncio
async def test_defensa_fallaste_http_exception_no_hay_intercambio(mock_juego_async, mock_atacante, mock_objetivo, mock_card_id, mock_proximo, mock_proximo2):
    mock_intercambio = None
    mock_juego_async.solicitud_intercambio = mock_intercambio
    mock_juego_async.jugadores_en_partida = [
        mock_atacante, mock_objetivo, mock_proximo, mock_proximo2]
    with pytest.raises(HTTPException) as exc:
        await defensa_fallaste(mock_juego_async, mock_objetivo, mock_atacante, mock_card_id)
    assert exc.value.status_code == 400
    assert exc.value.detail == "No hay solicitud de intercambio."
