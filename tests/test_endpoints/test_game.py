from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, Mock, MagicMock
from pony.orm import *
import pytest
from models.database_utils import *
from models.crud import *
from models.game import Juego

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


juego = AsyncMock()
juego.partida_id = 1
juego.cantidad_jugadores = 6
juego.creador = 3
juego.jugadores_id = [1, 2, 3, 4, 5, 6]


def test_jugar_carta_no_defensa(mocker, mock_juego):
    mocker.patch("endpoints.game.get_global_juego", return_value=mock_juego,
                 autospec=True,)
    mocker.patch("endpoints.game.get_jugador", return_value=mock_j1,
                 autospec=True,)
    mocker.patch("endpoints.game.check_turno", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.validar_jugada", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.check_puedo_defender", return_value=False,
                 autospec=True,)
    mocker.patch("endpoints.game.jugar_la_carta", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.broadcast_global", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.descartar_carta", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.check_ganador", return_value=False,
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.mensaje_personal", return_value=None,
                 autospec=True,)
    response = client.post("/game/play/attack", data={"match_id": 1,
                                                      "card_id": 22,
                                                      "player_objective": 2,
                                                      "player_orig": 1})
    assert response.status_code == 200
    assert response.json() == {"message": "Se jugó el ataque."}


def test_jugar_carta_con_defensa_recibir_ataque(mocker, mock_juego):
    mocker.patch("endpoints.game.get_global_juego", return_value=mock_juego,
                 autospec=True,)
    mocker.patch("endpoints.game.get_jugador", return_value=mock_j1,
                 autospec=True,)
    mocker.patch("endpoints.game.check_turno", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.validar_jugada", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.check_puedo_defender", return_value=True,
                 autospec=True,)
    mocker.patch("endpoints.game.crear_mensaje_de_ataque", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.mensaje_personal", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.mensaje_personal_dict", return_value=None,
                 autospec=True,)
    ###
    mocker.patch("endpoints.game.jugar_la_carta", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.responder_ataque", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.broadcast_global", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.check_ganador", return_value=False,
                 autospec=True,)
    response1 = client.post("/game/play/attack", data={"match_id": 1,
                                                       "card_id": 22,
                                                       "player_objective": 2,
                                                       "player_orig": 1})
    assert response1.status_code == 200
    assert response1.json() == {"message": "Se creó la solicitud de ataque."}
    response2 = client.post("/game/play/defense", data={"match_id": 1,
                                                        "card_id": 0,
                                                        "player_orig": 2})
    assert response2.status_code == 200
    assert response2.json() == {"message": "Se completó el ataque."}


def test_jugar_carta_con_defensa_no_recibir_ataque(mocker, mock_juego):
    mocker.patch("endpoints.game.get_global_juego", return_value=mock_juego,
                 autospec=True,)
    mocker.patch("endpoints.game.get_jugador", return_value=mock_j1,
                 autospec=True,)
    mocker.patch("endpoints.game.check_turno", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.validar_jugada", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.check_puedo_defender", return_value=True,
                 autospec=True,)
    mocker.patch("endpoints.game.crear_mensaje_de_ataque", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.mensaje_personal", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.mensaje_personal_dict", return_value=None,
                 autospec=True,)
    ###
    mocker.patch("endpoints.game.validar_carta", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.check_posibilidad_defensa", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.get_name_carta", return_value="pepe",
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.broadcast_global", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.responder_ataque", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.robar_carta_no_panico", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.check_ganador", return_value=False,
                 autospec=True,)
    response1 = client.post("/game/play/attack", data={"match_id": 1,
                                                       "card_id": 22,
                                                       "player_objective": 2,
                                                       "player_orig": 1})
    assert response1.status_code == 200
    assert response1.json() == {"message": "Se creó la solicitud de ataque."}
    response2 = client.post("/game/play/defense", data={"match_id": 1,
                                                        "card_id": 81,
                                                        "player_orig": 2})
    assert response2.status_code == 200
    assert response2.json() == {"message": "Se completó la defensa."}


#####
ganan_humanos = {'message': 'Ganan los Humanos', 'winners': [
    "humanos"], 'losers': ["la_cosa+infectados"]}
gana_la_cosa = {'message': 'Gana La Cosa', 'winners': [
    "la_cosa"], 'losers': ["infectados+humanos"]}
gana_cosa_infectados = {
    'message': 'Ganan La Cosa y Los Infectados',
    'winners': ["la_cosa+infectados"],
    'losers': ["humanos"]}
no_ganadores = "No hay ganadores."


def test_finalizar_partida_succes_humanos(mocker, mock_juego):
    mock_juego.cantidad_jugadores = 2
    mock_juego.jugadores_id = [1, 2]
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


def test_finalizar_partida_succes_lacosa(mocker, mock_juego):
    mock_juego.cantidad_jugadores = 2
    mock_juego.jugadores_id = [1, 2]
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


def test_finalizar_partida_succes_lacosa_infectados(mocker, mock_juego):
    mock_juego.cantidad_jugadores = 2
    mock_juego.jugadores_id = [1, 2]
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


def test_finalizar_partida_fail(mocker, mock_juego):
    mock_juego.cantidad_jugadores = 2
    mock_juego.jugadores_id = [1, 2]
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
        'detail': "Error: " + no_ganadores}


def test_endpoint_descartar_carta_success(mocker, mock_juego, mock_j1):
    mock_juego.cantidad_jugadores = 2
    mock_juego.jugadores_id = [1, 2]
    mock_j1.mano = [1, 2, 3, 4]
    mocker.patch("endpoints.game.get_global_juego", return_value=mock_juego,
                 autospec=True)
    mocker.patch("endpoints.game.descartar_carta", return_value=True,
                 autoespec=True,)
    mocker.patch("endpoints.game.Juego.mensaje_personal", return_value=True,
                 autoespec=True,)

    response = client.post("/game/discard", data={"match_id": 1,
                                                  "card_id": 2,
                                                  "player_id": 1})
    assert response.status_code == 200
    assert response.json() == {"carta descartada": 2}


def test_endpoint_descartar_carta_fail(mocker):
    mocker.patch("endpoints.game.get_global_juego", return_value=juego,
                 autospec=True)
    mocker.patch("endpoints.game.descartar_carta", return_value=True,
                 autoespec=True,)
    response = client.post("/game/discard", data={"match_id": "a",
                                                  "card_id": 2,
                                                  "player_id": 1})
    assert response.status_code == 422


def test_swap_request_success(mocker, mock_juego):
    mocker.patch("endpoints.game.get_global_juego", return_value=mock_juego,
                 autospec=True,)
    mocker.patch("endpoints.game.get_jugador", return_value=mock_j1,
                 autospec=True,)
    mocker.patch("endpoints.game.check_turno", return_value=True,
                 autospec=True,)
    mocker.patch("endpoints.game.check_carta_habilitada", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.terminar_turno", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.avanzar_turno", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.get_jugador_en_turno",
                 return_value=mock_j1, autospec=True,)
    mocker.patch("endpoints.game.check_objetive_is_next", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.check_obstaculo", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.crear_intercambio", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.mensaje_personal", return_value=None,
                 autospec=True,)

    response = client.post("/game/swap-request", data={"match_id": 1,
                                                       "card_id": 2,
                                                       "player_objective": 3,
                                                       "player_orig": 2})
    assert response.status_code == 200
    assert response.json() == {
        "message": "se creo la solicitud de intercambio"}


def test_swap_request_fail(mocker, mock_juego):
    mocker.patch("endpoints.game.get_global_juego", return_value=mock_juego,
                 autospec=True,)
    mocker.patch("endpoints.game.get_jugador", return_value=mock_j1,
                 autospec=True,)
    mocker.patch("endpoints.game.check_turno", side_effect=HTTPException(
        status_code=400, detail="No es el turno del jugador"), autospec=True,)
    response = client.post("/game/swap-request", data={"match_id": 1,
                                                       "card_id": 2,
                                                       "player_objective": 3,
                                                       "player_orig": 2})
    assert response.status_code == 400
    assert response.json() == {"detail": "Error: No es el turno del jugador"}


def test_swap_response_success(mocker, mock_juego):
    mocker.patch("endpoints.game.get_global_juego", return_value=mock_juego,
                 autospec=True,)
    mocker.patch("endpoints.game.get_jugador", return_value=mock_j1,
                 autospec=True,)
    mocker.patch("endpoints.game.check_carta_habilitada", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.check_ganador", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.responder_intercambio",
                 return_value=None, autospec=True,)
    mocker.patch("endpoints.game.Juego.mensaje_personal", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.broadcast_global", return_value=None,
                 autospec=True,)

    response = client.post("/game/swap-response", data={"match_id": 1,
                                                        "card_id": 2,
                                                        "player_objective": 3,
                                                        "player_orig": 2})
    assert response.status_code == 200
    assert response.json() == {"message": "se completo el intercambio"}


def test_swap_response_fail(mocker, mock_juego):
    mocker.patch("endpoints.game.get_global_juego", return_value=mock_juego,
                 autospec=True,)
    mocker.patch("endpoints.game.get_jugador", return_value=mock_j1,
                 autospec=True,)
    mocker.patch(
        "endpoints.game.check_carta_habilitada",
        side_effect=HTTPException(
            status_code=400,
            detail="No puedes descartar la unica carta de infectado que tienes."),
        autospec=True,
    )
    mocker.patch("endpoints.game.check_ganador", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.responder_intercambio",
                 return_value=None, autospec=True,)
    mocker.patch("endpoints.game.Juego.mensaje_personal", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.broadcast_global", return_value=None,
                 autospec=True,)

    response = client.post("/game/swap-response", data={"match_id": 1,
                                                        "card_id": 2,
                                                        "player_objective": 3,
                                                        "player_orig": 2})
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Error: No puedes descartar la unica carta de infectado que tienes."}
