from unittest.mock import Mock, AsyncMock
from fastapi.testclient import TestClient
import pytest
from models.lobby_models import Lobby
from main import app

client = TestClient(app)

mocker = Mock()


def test_add_player():
    lobby = Lobby(1, "test_lobby", None, 4, 2, 1)
    assert lobby.cantidad_jugadores == 1
    lobby.add_player(2)
    assert lobby.cantidad_jugadores == 2
    assert lobby.users_id == [1, 2]


def test_remove_player():
    lobby = Lobby(1, "test_lobby", None, 4, 2, 1)
    lobby.add_player(2)
    lobby.add_player(3)
    assert lobby.cantidad_jugadores == 3
    lobby.remove_player(2)
    assert lobby.cantidad_jugadores == 2
    assert lobby.users_id == [1, 3]


def test_list_players():
    lobby = Lobby(1, "test_lobby", None, 4, 2, 1)
    lobby.add_player(2)
    lobby.add_player(3)
    assert lobby.list_players() == [1, 2, 3]


# def test_init_game(mocker):
#     lobby = Lobby(1, "test_lobby", None, 4, 2, 1)
#     lobby.add_player(2)
#     lobby.add_player(3)
#     mocker.patch(
#         'models.lobby_models.Juego.repartir_cartas',
#         return_value=None,
#         autospec=True)
#     lobby.init_game()
#     assert lobby.iniciada
