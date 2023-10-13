from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, Mock, MagicMock
from pony.orm import *
from models.database_utils import *
from models.crud import *

from main import app
client = TestClient(app)

mocked_juego = MagicMock()
mocked_juego.partida_id = 1
mocked_juego.cantidad_jugadores = 4
mocked_juego.creador = 1
mocked_juego.jugadores_id = [1, 2, 3, 4]

mocker = Mock()
juego = AsyncMock()
juego.partida_id = 1
juego.cantidad_jugadores = 6
juego.creador = 3
juego.jugadores_id = [1,2,3,4,5,6]

def test_jugar_carta_success(mocker):
    mocker.patch("endpoints.game.get_global_juego", return_value = juego, 
                 autospec = True,)
    mocker.patch("endpoints.game.jugar_la_carta", return_value = True, 
                 autospec = True,)
    mocker.patch("endpoints.game.descartar_carta", return_value = True, 
                 autospec = True,)
    mocker.patch("endpoints.game.Juego.broadcast_global", return_value = None, 
                 autospec = True,)
    response = client.post("/game/play", data = {"match_id" : 1, 
                                                  "card_id" : 2,
                                                  "player_objective" : 3, 
                                                  "player_orig" : 2})
    assert response.status_code == 200
    assert response.json() == {"carta": 2, "jugada contra": 3, "por": 2}


def test_jugar_carta_success1(mocker):
    mocker.patch("endpoints.game.get_global_juego", return_value = juego, 
                 autospec = True,)
    mocker.patch("endpoints.game.jugar_la_carta", return_value = True, 
                 autospec = True,)
    mocker.patch("endpoints.game.descartar_carta", return_value = False, 
                 autospec = True,)
    response = client.post("/game/play", data = {"match_id" : 1, 
                                                  "card_id" : 2,
                                                  "player_objective" : 3, 
                                                  "player_orig" : 2})
    assert response.status_code == 200
    #assert response.json() == {"error al jugar la carta": 2, "contra": 3, "por": 2}


def test_jugar_carta_fail(mocker):
    mocker.patch("endpoints.game.get_global_juego", return_value = juego, 
                 autospec = True,)
    mocker.patch("endpoints.game.jugar_la_carta", return_value = True, 
                 autospec = True,)
    mocker.patch("endpoints.game.descartar_carta", return_value = False, 
                 autospec = True,)
    response = client.post("/game/play", data = {"match_id" : "a", 
                                                  "card_id" : 2,
                                                  "player_objective" : 3, 
                                                  "player_orig" : 2})
    assert response.status_code == 422
    