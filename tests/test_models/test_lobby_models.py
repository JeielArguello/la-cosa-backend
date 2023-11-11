import asyncio
from unittest.mock import AsyncMock, Mock, patch
from fastapi.testclient import TestClient
import pytest
from models.lobby_models import Lobby
from main import app
from models.player import JugadorPartida
from utils.game_utils import global_juegos

client = TestClient(app)

mocker = Mock()


@pytest.fixture
def lobby():
    lobby = Lobby(1, "test_lobby", None, 4, 2, 1)
    return lobby


# @pytest.fixture
# def mock_j1(mocker):
#     mocker.patch("models.player.get_name", return_value="pepe")
#     jugador = JugadorPartida(id=1)
#     return jugador


# @pytest.fixture
# def mock_j2(mocker):
#     mocker.patch("models.player.get_name", return_value="pedro")
#     jugador = JugadorPartida(id=2)
#     return jugador


# @pytest.fixture
# def mock_j3(mocker):
#     mocker.patch("models.player.get_name", return_value="jose")
#     jugador = JugadorPartida(id=1)
#     return jugador


def test_add_player_lobby_ok(lobby):
    assert lobby.cantidad_jugadores == 1
    lobby.add_player(2)
    assert lobby.cantidad_jugadores == 2
    assert lobby.users_id == [1, 2]


def test_remove_player_lobby_ok(lobby):
    lobby.add_player(2)
    lobby.add_player(3)
    assert lobby.cantidad_jugadores == 3
    lobby.remove_player(2)
    assert lobby.cantidad_jugadores == 2
    assert lobby.users_id == [1, 3]


def test_list_players_lobby_ok(lobby):
    lobby.add_player(2)
    lobby.add_player(3)
    assert lobby.list_players() == [1, 2, 3]


@pytest.mark.asyncio
async def test_init_game_ok(mocker, lobby):
    lobby.add_player(2)
    lobby.add_player(3)
    mocker.patch(
        'models.lobby_models.Juego.repartir_cartas',
        return_value=None,
        autospec=True)
    mocker.patch("models.player.get_name", return_value="pepe")
    mocker.patch("models.player.get_id_avatar", return_value=1)
    await lobby.init_game()
    assert len(global_juegos) == 1
    assert lobby.iniciada
