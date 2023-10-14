from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, Mock, MagicMock
from pony.orm import *
from models.database_utils import *
from models.crud import *
from models.game import Juego

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
juego.jugadores_id = [1, 2, 3, 4, 5, 6]


def test_jugar_carta_success(mocker):
    mocker.patch("endpoints.game.get_global_juego", return_value=juego,
                 autospec=True,)
    mocker.patch("endpoints.game.jugar_la_carta", return_value=True,
                 autospec=True,)
    mocker.patch("endpoints.game.descartar_carta", return_value=True,
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.broadcast_global", return_value=None,
                 autospec=True,)

    response = client.post("/game/play", data={"match_id": 1,
                                               "card_id": 2,
                                               "player_objective": 3,
                                               "player_orig": 2})
    assert response.status_code == 200
    assert response.json() == {"carta": 2, "jugada contra": 3, "por": 2}


def test_jugar_carta_success1(mocker):
    mocker.patch("endpoints.game.get_global_juego", return_value=juego,
                 autospec=True,)
    mocker.patch("endpoints.game.jugar_la_carta", return_value=True,
                 autospec=True,)
    mocker.patch("endpoints.game.descartar_carta", return_value=False,
                 autospec=True,)
    response = client.post("/game/play", data={"match_id": 1,
                                               "card_id": 2,
                                               "player_objective": 3,
                                               "player_orig": 2})
    assert response.status_code == 200
    # assert response.json() == {"error al jugar la carta": 2, "contra": 3, "por": 2}


def test_jugar_carta_fail(mocker):
    mocker.patch("endpoints.game.get_global_juego", return_value=juego,
                 autospec=True,)
    mocker.patch("endpoints.game.jugar_la_carta", return_value=True,
                 autospec=True,)
    mocker.patch("endpoints.game.descartar_carta", return_value=False,
                 autospec=True,)
    response = client.post("/game/play", data={"match_id": "a",
                                               "card_id": 2,
                                               "player_objective": 3,
                                               "player_orig": 2})
    assert response.status_code == 422


#####
ganan_humanos = {'message': 'Ganan los Humanos', 'winners': [
    "humanos"], 'losers': ["la_cosa+infectados"]}
gana_la_cosa = {'message': 'Gana La Cosa', 'winners': [
    "la_cosa"], 'losers': ["infectados+humanos"]}
gana_cosa_infectados = {'message': 'Ganan La Cosa y Los Infectados', 'winners': [
    "la_cosa+infectados"], 'losers': ["humanos"]}
no_ganadores = "No hay ganadores."


def test_finalizar_partida_succes_humanos(mocker):
    mock_juego = Juego(partida_id=1, cantidad_jugadores=2,
                       creador=1, jugadores_id=[1, 2])
    mocker.patch('endpoints.game.get_global_juego',
                 return_value=mock_juego, autospec=True)
    mocker.patch('endpoints.game.finalizar_juego',
                 return_value=ganan_humanos, autospec=True)
    mocker.patch('endpoints.game.delete_global_juego',
                 return_value=True, autospec=True)
    mocker.patch('endpoints.game.delete_match',
                 return_value=True, autospec=True)

    response = client.post("/game/finish", data={"match_id": 1})
    assert response.status_code != 422, "Los parametros de entrada del endpoint no pueden ser procesados"
    assert response.status_code == 200
    assert response.json() == ganan_humanos


def test_finalizar_partida_succes_lacosa(mocker):
    mock_juego = Juego(partida_id=1, cantidad_jugadores=2,
                       creador=1, jugadores_id=[1, 2])
    mocker.patch('endpoints.game.get_global_juego',
                 return_value=mock_juego, autospec=True)
    mocker.patch('endpoints.game.finalizar_juego',
                 return_value=gana_la_cosa, autospec=True)
    mocker.patch('endpoints.game.delete_global_juego',
                 return_value=True, autospec=True)
    mocker.patch('endpoints.game.delete_match',
                 return_value=True, autospec=True)

    response = client.post("/game/finish", data={"match_id": 1})
    assert response.status_code != 422, "Los parametros de entrada del endpoint no pueden ser procesados"
    assert response.status_code == 200
    assert response.json() == gana_la_cosa


def test_finalizar_partida_succes_lacosa_infectados(mocker):
    mock_juego = Juego(partida_id=1, cantidad_jugadores=2,
                       creador=1, jugadores_id=[1, 2])
    mocker.patch('endpoints.game.get_global_juego',
                 return_value=mock_juego, autospec=True)
    mocker.patch('endpoints.game.finalizar_juego',
                 return_value=gana_cosa_infectados, autospec=True)
    mocker.patch('endpoints.game.delete_global_juego',
                 return_value=True, autospec=True)
    mocker.patch('endpoints.game.delete_match',
                 return_value=True, autospec=True)

    response = client.post("/game/finish", data={"match_id": 1})
    assert response.status_code != 422, "Los parametros de entrada del endpoint no pueden ser procesados"
    assert response.status_code == 200
    assert response.json() == gana_cosa_infectados


def test_finalizar_partida_fail(mocker):
    mock_juego = Juego(partida_id=1, cantidad_jugadores=2,
                       creador=1, jugadores_id=[1, 2])
    mocker.patch('endpoints.game.get_global_juego',
                 return_value=mock_juego, autospec=True)
    mocker.patch(
        'endpoints.game.finalizar_juego',
        side_effect=HTTPException(
            status_code=400,
            detail=no_ganadores),
        autospec=True)

    response = client.post("/game/finish", data={"match_id": 1})
    assert response.status_code != 422, "Los parametros de entrada del endpoint no pueden ser procesados"
    assert response.status_code == 400
    assert response.json() == {
        'detail': "Error: "+no_ganadores}
