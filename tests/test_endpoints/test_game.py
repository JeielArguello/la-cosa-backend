from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, Mock, MagicMock
from pony.orm import *
import pytest
from models.database_utils import *
from models.crud import *
from models.game import Juego

from main import app
from models.player import JugadorPartida
from models.swap_card import IntercambiarCarta, IntercambiarCartaVyv
client = TestClient(app)

mocker = Mock()


@pytest.fixture
def mock_j1(mocker):
    mocker.patch("models.player.get_name", return_value="pepe")
    mocker.patch("models.player.get_id_avatar", return_value=1)
    jugador = JugadorPartida(id=1)
    jugador.turno_actual = True
    jugador.cartas = [1, 2, 3, 4]
    return jugador

@pytest.fixture
def mock_j2(mocker):
    mocker.patch("models.player.get_name", return_value="pedro")
    mocker.patch("models.player.get_id_avatar", return_value=2)
    jugador = JugadorPartida(id=2)
    return jugador

@pytest.fixture
def mock_intercambio(mock_j1, mock_j2):
    swap_card = IntercambiarCarta(mock_j1, 1, mock_j2)    
    return swap_card

@pytest.fixture
def mock_juego(mocker, mock_intercambio):
    mocker.patch("models.player.get_name", return_value="pepe")
    juego = Juego(partida_id=1, cantidad_jugadores=4,
                  creador=1, jugadores_id=[1, 3, 2, 4])
    juego.name = "test"
    juego.posiciones = [1, 0, 2, 0, 3, 0, 4, 0]
    juego.solicitud_intercambio = mock_intercambio
    return juego

juego = AsyncMock()
juego.partida_id = 1
juego.cantidad_jugadores = 6
juego.creador = 3
juego.jugadores_id = [1, 2, 3, 4, 5, 6]


def test_robar_carta_panico_200_ok(mocker, mock_juego, mock_j1):
    mock_juego.mazo = [105]
    mock_juego.mazo_descarte = []
    mocker.patch("endpoints.game.get_global_juego", return_value=mock_juego,
                 autospec=True,)
    mocker.patch("endpoints.game.get_jugador", return_value=mock_j1,
                 autospec=True,)
    mocker.patch("endpoints.game.check_carta_panico", return_value=True,
                 autospec=True,)
    mocker.patch("endpoints.game.jugar_panico", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.broadcast_global", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.get_jugador_siguiente_turno", return_value=mock_j1,
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.is_obstaculo", return_value=True,
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.mensaje_personal", return_value=None,
                 autospec=True,)
    response = client.post("/game/pick", data={"match_id": 1,
                                               "player_id": 1})
    assert response.status_code == 200
    assert response.json() == {'card_id': 105}


def test_robar_carta_no_panico_200_ok(mocker, mock_juego, mock_j1):
    mock_juego.mazo = [22]
    mocker.patch("endpoints.game.get_global_juego", return_value=mock_juego,
                 autospec=True,)
    mocker.patch("endpoints.game.get_jugador", return_value=mock_j1,
                 autospec=True,)
    mocker.patch("endpoints.game.check_carta_panico", return_value=False,
                 autospec=True,)
    mocker.patch("endpoints.game.robar_carta", return_value=22,
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.broadcast_global", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.mensaje_personal", return_value=None,
                 autospec=True,)
    response = client.post("/game/pick", data={"match_id": 1,
                                               "player_id": 1})
    assert response.status_code == 200
    assert response.json() == {'card_id': 22}


def test_robar_carta_400_no_juego(mocker, mock_juego, mock_j1):
    mocker.patch(
        'endpoints.game.get_global_juego',
        side_effect=HTTPException(
            status_code=400,
            detail="No se pudo acceder al juego"),
        autospec=True)
    response = client.post("/game/pick", data={"match_id": 1,
                                               "player_id": 1})
    assert response.status_code == 400
    assert response.json() == {'detail': 'Error: No se pudo acceder al juego'}


def test_jugar_carta_sin_defensa_200_ok(mocker, mock_juego, mock_j1):
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
    mocker.patch("endpoints.game.Juego.is_obstaculo", return_value=False,
                 autospec=True,)
    response = client.post("/game/play/attack", data={"match_id": 1,
                                                      "card_id": 22,
                                                      "player_objective": 2,
                                                      "player_orig": 1})
    assert response.status_code == 200
    assert response.json() == {"message": "Se jugó el ataque."}


def test_jugar_carta_con_defensa_recibir_ataque_200_ok(mocker, mock_juego):
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


def test_jugar_carta_con_defensa_no_recibir_ataque_200_ok(mocker, mock_juego, mock_j1: JugadorPartida):
    jugador = mock_j1
    jugador.cartas = [1, 2, 3, 81]
    mock_j1.cartas = [1, 2, 3, 81]
    mocker.patch("endpoints.game.get_global_juego", return_value=mock_juego,
                 autospec=True,)
    mocker.patch("endpoints.game.get_jugador", return_value=None,
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
    mocker.patch("endpoints.game.Juego.is_obstaculo", return_value=True,
                 autospec=True,)
    response1 = client.post("/game/play/attack", data={"match_id": 1,
                                                       "card_id": 22,
                                                       "player_objective": 2,
                                                       "player_orig": 1})
    assert response1.status_code == 200
    assert response1.json() == {"message": "Se creó la solicitud de ataque."}
    mocker.patch("endpoints.game.Juego.get_jugador", side_effect={mock_j1, jugador},
                 autospec=True,)
    response2 = client.post("/game/play/defense", data={"match_id": 1,
                                                        "card_id": 81,
                                                        "player_orig": 2})
    assert response2.status_code == 200
    assert response2.json() == {"message": "Se completó la defensa."}


def test_jugar_carta_ataque_400_no_juego(mocker, mock_juego, mock_j1):
    mocker.patch(
        'endpoints.game.get_global_juego',
        side_effect=HTTPException(
            status_code=400,
            detail="No se pudo acceder al juego"),
        autospec=True)
    response = client.post("/game/play/attack", data={"match_id": 1,
                                                      "card_id": 22,
                                                      "player_objective": 2,
                                                      "player_orig": 1})
    assert response.status_code == 400
    assert response.json() == {'detail': 'Error: No se pudo acceder al juego'}


def test_jugar_carta_defense_400_no_puedes_defenderte(mocker, mock_juego, mock_j1):
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
    mocker.patch(
        'endpoints.game.check_posibilidad_defensa',
        side_effect=HTTPException(
            status_code=400,
            detail="Esta carta no puede defenderte."),
        autospec=True)

    response1 = client.post("/game/play/attack", data={"match_id": 1,
                                                       "card_id": 22,
                                                       "player_objective": 2,
                                                       "player_orig": 1})
    assert response1.status_code == 200
    assert response1.json() == {"message": "Se creó la solicitud de ataque."}
    response2 = client.post("/game/play/defense", data={"match_id": 1,
                                                        "card_id": 81,
                                                        "player_orig": 2})
    assert response2.status_code == 400
    assert response2.json() == {
        'detail': 'Error: Esta carta no puede defenderte.'}


def test_descartar_carta_200_ok(mocker, mock_juego, mock_j1):
    mock_juego.cantidad_jugadores = 2
    mock_juego.jugadores_id = [1, 2]
    mock_j1.mano = [1, 2, 3, 4]
    mocker.patch("endpoints.game.get_global_juego", return_value=mock_juego,
                 autospec=True)
    mocker.patch("endpoints.game.descartar_carta", return_value=True,
                 autoespec=True,)
    mocker.patch("endpoints.game.Juego.mensaje_personal", return_value=True,
                 autoespec=True,)
    mocker.patch("endpoints.game.Juego.is_obstaculo", return_value=True,
                 autospec=True,)
    response = client.post("/game/discard", data={"match_id": 1,
                                                  "card_id": 2,
                                                  "player_id": 1})
    assert response.status_code == 200
    assert response.json() == {"carta descartada": 2}


def test_descartar_carta_400_no_tiene_la_carta(mocker, mock_juego, mock_j1):
    mocker.patch("endpoints.game.get_global_juego", return_value=mock_juego,
                 autospec=True,)
    mocker.patch("endpoints.game.get_jugador", return_value=mock_j1,
                 autospec=True,)
    mocker.patch(
        'endpoints.game.descartar_carta',
        side_effect=HTTPException(
            status_code=400,
            detail="El jugador no posee esta carta"),
        autospec=True)
    response = client.post("/game/discard", data={"match_id": 1,
                                                  "card_id": 2,
                                                  "player_id": 1})
    assert response.status_code == 400
    assert response.json() == {
        'detail': 'Error: El jugador no posee esta carta'}


def test_swap_request_200_ok(mocker, mock_juego):
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


def test_swap_request_400_no_turno(mocker, mock_juego):
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


def test_swap_response_200_ok(mocker, mock_juego):
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
    mocker.patch("endpoints.game.mostrar_cartas_cuarentena", return_value=None,
                 autospec=True,)
    

    response = client.post("/game/swap-response", data={"match_id": 1,
                                                        "card_id": 2,
                                                        "player_objective": 3,
                                                        "player_orig": 2,
                                                        "se_defiende": False})
    assert response.status_code == 200
    assert response.json() == {"message": "se completo el intercambio"}


def test_swap_response_400_infectado_no_cambia_carta_infectado(mocker, mock_juego):
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
                                                        "player_orig": 2,
                                                        "se_defiende": False})
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Error: No puedes descartar la unica carta de infectado que tienes."}


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


def test_finalizar_partida_200_ok_ganan_humanos(mocker, mock_juego):
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


def test_finalizar_partida_200_ok_gana_la_cosa(mocker, mock_juego):
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


def test_finalizar_partida_200_ok_gana_la_cosa_e_infectados(mocker, mock_juego):
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


def test_finalizar_partida_400_no_hay_ganadores(mocker, mock_juego):
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


def test_decretar_finalizar_partida_200_ok_gana_la_cosa_e_infectados(mocker, mock_juego):
    mocker.patch('endpoints.game.get_global_juego',
                 return_value=mock_juego, autospec=True)
    mocker.patch("endpoints.game.get_jugador", return_value=mock_j1,
                 autospec=True,)
    mocker.patch('endpoints.game.check_la_cosa',
                 return_value=True, autospec=True)
    mocker.patch('endpoints.game.finalizar_juego',
                 return_value=gana_cosa_infectados, autospec=True)
    mocker.patch('endpoints.game.delete_global_juego',
                 return_value=True, autospec=True)
    mocker.patch('endpoints.game.delete_match',
                 return_value=True, autospec=True)
    mocker.patch('endpoints.game.Juego.broadcast_global',
                 return_value=True, autospec=True)

    response = client.post("/game/finish/thething",
                           data={"match_id": 1, "player_id": 1})
    assert response.status_code != 422, "Los parametros de entrada del endpoint no pueden ser procesados"
    assert response.status_code == 200
    assert response.json() == gana_cosa_infectados


def test_decretar_finalizar_partida_200_ok_ganan_humanos(mocker, mock_juego):
    mocker.patch('endpoints.game.get_global_juego',
                 return_value=mock_juego, autospec=True)
    mocker.patch("endpoints.game.get_jugador", return_value=mock_j1,
                 autospec=True,)
    mocker.patch('endpoints.game.check_la_cosa',
                 return_value=True, autospec=True)
    mocker.patch('endpoints.game.finalizar_juego',
                 return_value=ganan_humanos, autospec=True)
    mocker.patch('endpoints.game.delete_global_juego',
                 return_value=True, autospec=True)
    mocker.patch('endpoints.game.delete_match',
                 return_value=True, autospec=True)
    mocker.patch('endpoints.game.Juego.broadcast_global',
                 return_value=True, autospec=True)

    response = client.post("/game/finish/thething",
                           data={"match_id": 1, "player_id": 1})
    assert response.status_code != 422, "Los parametros de entrada del endpoint no pueden ser procesados"
    assert response.status_code == 200
    assert response.json() == ganan_humanos


def test_decretar_finalizar_partida_400_no_eres_la_cosa(mocker, mock_juego):
    mocker.patch('endpoints.game.get_global_juego',
                 return_value=mock_juego, autospec=True)
    mocker.patch("endpoints.game.get_jugador", return_value=mock_j1,
                 autospec=True,)
    response = client.post("/game/finish/thething",
                           data={"match_id": 1, "player_id": 1})
    assert response.status_code != 422, "Los parametros de entrada del endpoint no pueden ser procesados"
    assert response.status_code == 400
    assert response.json() == {'detail': 'Error: El jugador no es la cosa.'}


def test_seleccionar_carta_determinacion_200_ok(mocker, mock_juego):
    mocker.patch("endpoints.game.get_global_juego", return_value=mock_juego,
                 autospec=True,)
    mocker.patch("endpoints.game.get_jugador", return_value=mock_j1,
                 autospec=True,)
    mocker.patch("endpoints.game.check_turno", return_value=True,
                 autospec=True,)
    mocker.patch("endpoints.game.agregar_carta_determinacion", return_value=True,
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.mensaje_personal", return_value=None,
                 autospec=True,)

    response = client.post("game/play/determination", data={"match_id": 1,
                                                            "card_id": 2,
                                                            "player_id": 1})
    assert response.status_code == 200
    assert response.json() == {"carta elegida": 2}


def test_seleccionar_carta_determinacion_400_no_es_tu_turno(mocker, mock_juego):
    mocker.patch("endpoints.game.get_global_juego", return_value=mock_juego,
                 autospec=True,)
    mocker.patch("endpoints.game.get_jugador", return_value=mock_j1,
                 autospec=True,)
    mocker.patch("endpoints.game.check_turno", side_effect=HTTPException(status_code=400, detail="No es el turno del jugador"),
                 autospec=True,)
    mocker.patch("endpoints.game.agregar_carta_determinacion", return_value=True,
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.mensaje_personal", return_value=None,
                 autospec=True,)

    response = client.post("game/play/determination", data={"match_id": 1,
                                                            "card_id": 2,
                                                            "player_id": 1})
    assert response.status_code == 400
    assert response.json() == {"detail": "Error: No es el turno del jugador"}


def test_get_logs_200_ok(mocker, mock_juego):
    mock_juego.logs = ["test logs", "testeando logs", "se testearon los logs"]
    mocker.patch("endpoints.game.get_global_juego", return_value=mock_juego,
                 autospec=True,)
    response = client.get('/game/log/1')
    assert response.status_code == 200
    assert response.json() == {
        "logs": ["test logs", "testeando logs", "se testearon los logs"]}


def test_get_logs_400_no_juego(mocker, mock_juego):
    response = client.get('/game/log/1')
    assert response.status_code == 400
    assert response.json() == {'detail': 'Error: No se pudo acceder al juego'}




def test_endpoint_vuelta_y_vuelta_200_ok_no_completo(mocker, mock_juego, mock_j1,mock_j2):
    juego = mock_juego
    juego.solicitud_intercambio_vyv = IntercambiarCartaVyv(mock_j1, 2)
    jugador1 = mock_j1
    jugador1.cartas = [10, 23, 30, 40]
    mocker.patch("endpoints.game.get_global_juego", return_value=juego,
                 autospec=True,)
    mocker.patch("endpoints.game.get_jugador", return_value=jugador1,
                 autospec=True,)
    mocker.patch("endpoints.game.check_turno", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.get_jugador_siguiente_turno", return_value=mock_j2,
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.mensaje_personal", return_value=None,
                 autospec=True,)
    response = client.post("/game/play/vuelta_y_vuelta", data={"match_id": 1,
                                                                "card_id": 23,
                                                                "player_orig": 1})
    assert response.json() == {"resultado": "El jugador pepe selecciono una carta correctamente."}
    assert response.status_code == 200

def test_endpoint_vuelta_y_vuelta_200_ok_completo(mocker, mock_juego, mock_j1,mock_j2):
    juego: Juego = mock_juego
    jugador1: JugadorPartida = mock_j1
    jugador2: JugadorPartida = mock_j2
    jugador1.cartas = [10, 22, 30, 40]
    jugador2.cartas = [11, 12, 23, 14]
    juego.solicitud_intercambio_vyv = IntercambiarCartaVyv(jugador1, 2)
    juego.solicitud_intercambio_vyv.completar_vuelta_y_vuelta(jugador1, 22)
    juego.jugadores_en_partida = [jugador1, jugador2]
    mocker.patch("endpoints.game.get_global_juego", return_value=juego,
                 autospec=True,)
    mocker.patch("endpoints.game.check_turno", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.check_carta_habilitada", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.get_jugador_siguiente", return_value=mock_j1,
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.get_jugador_siguiente_turno", return_value=mock_j1,
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.terminar_turno", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.avanzar_turno", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.broadcast_global", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.mensaje_personal", return_value=None,
                 autospec=True,)
    response = client.post("/game/play/vuelta_y_vuelta", data={"match_id": 1,
                                                               "card_id": 23,
                                                               "player_orig": 2})
    assert response.json() == {"resultado": "Se completo el intercambio vuelta y vuelta correctamente"}
    assert response.status_code == 200

def test_endpoint_vuelta_y_vuelta_carta_no_habilitada(mocker, mock_juego, mock_j1):
    mock_juego.solicitud_intercambio_vyv = IntercambiarCartaVyv(mock_j1, 1)
    mocker.patch("endpoints.game.get_global_juego", return_value=mock_juego,
                 autospec=True,)
    mocker.patch("endpoints.game.get_jugador", return_value=mock_j1,
                 autospec=True,)
    mocker.patch("endpoints.game.check_turno", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.check_carta_habilitada", side_effect=HTTPException(
            status_code=400,
            detail="No puedes descartar la carta la cosa."),
                 autospec=True,)
    response = client.post("/game/play/vuelta_y_vuelta", data={"match_id": 1,
                                                               "card_id": 10,
                                                               "player_orig": 1})
    assert response.json() == {'detail': 'Error: No puedes descartar la carta la cosa.'}
    assert response.status_code == 400


def test_endpoint_olvidadizo_200_ok(mocker, mock_juego, mock_j1):
    juego: Juego = mock_juego
    jugador1: JugadorPartida = mock_j1
    jugador1.cartas = [1, 10, 20, 30]
    jugador2: JugadorPartida = mock_j1
    jugador2.name = "pablo"
    mocker.patch("endpoints.game.get_global_juego", return_value = juego, autospec = True)
    mocker.patch("endpoints.game.check_turno", return_value = True, autospec = True)
    mocker.patch("endpoints.game.Juego.mensaje_personal", return_value = None, autospec = True)
    mocker.patch("endpoints.game.Juego.get_jugador_siguiente_turno", return_value = jugador2, autospec = True)
    juego.jugadores_en_partida= [jugador1,jugador2]
    
    response = client.post("game/play/olvidadizo",data ={"match_id":1, 
                                                     "card_id_elegida":30, 
                                                     "player_id": 1})
    assert response.status_code == 200
    assert response.json() == {"mensaje":"carta olvidadizo jugada"}


def test_olvidadizo_endpoint_jugador_no_en_turno(mocker, mock_juego, mock_j1): 
    juego: Juego = mock_juego
    jugador1: JugadorPartida = mock_j1
    jugador1.cartas = [1, 10, 20, 30]
    mocker.patch("endpoints.game.get_global_juego", return_value = juego, autospec = True)
    mocker.patch("endpoints.game.check_turno", side_effect=HTTPException(status_code=400, detail="No es el turno del jugador"),
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.mensaje_personal", return_value = None, autospec = True)
    juego.jugadores_en_partida= [jugador1]
    
    response = client.post("game/play/olvidadizo",data ={"match_id":1, 
                                                     "card_id_elegida":30, 
                                                     "player_id": 1})
    assert response.status_code == 400
    assert response.json() == {"detail": "Error: No es el turno del jugador"}
    


def test_que_quede_entre_nosotros_endpoint_200_ok(mocker, mock_juego, mock_j1, mock_j2):
    juego: Juego = mock_juego
    jugador1: JugadorPartida = mock_j1
    jugador2: JugadorPartida = mock_j2
    jugador1.cartas = [10, 20, 30, 40]
    mocker.patch("endpoints.game.get_global_juego", return_value = juego, autospec = True)
    mocker.patch("endpoints.game.check_turno", return_value = True, autospec = True,)
    mocker.patch("endpoints.game.Juego.mensaje_personal", return_value = None, autospec = True)
    juego.jugadores_en_partida= [jugador1, jugador2]
    response = client.post("game/play/que_quede_entre_nosotros", data ={"match_id": 1, "player_objective":2, "player_orig": 1})
    assert response.status_code == 200
    assert response.json()["mensaje"]["cartaMostrar"] == [{"id": 10},{"id": 20},{"id": 30},{"id":40}]
        
   
   
def test_que_quede_entre_nosotros_endpoint_jugador_no_en_turno(mocker, mock_juego, mock_j1, mock_j2):
    juego: Juego = mock_juego
    jugador1: JugadorPartida = mock_j1
    jugador2: JugadorPartida = mock_j2
    jugador1.cartas = [10, 20, 30, 40]
    mocker.patch("endpoints.game.get_global_juego", return_value = juego, autospec = True)
    mocker.patch("endpoints.game.check_turno", side_effect=HTTPException(status_code=400, detail="No es el turno del jugador"),
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.mensaje_personal", return_value = None, autospec = True)
    juego.jugadores_en_partida= [jugador1, jugador2]
    response = client.post("game/play/que_quede_entre_nosotros", data ={"match_id": 1, "player_objective":2, "player_orig": 1})
    assert response.status_code == 400
    assert response.json() == {"detail": "Error: No es el turno del jugador"}


##Test endpoints No podemos ser amigos-request y response.
def test_no_podemos_ser_amigos_endpoint_request_200_ok(mocker, mock_juego, mock_j1, mock_j2):
    juego: Juego = mock_juego
    jugador_solicitante: JugadorPartida = mock_j1
    jugador_solicitado: JugadorPartida = mock_j2
    mocker.patch("endpoints.game.get_global_juego", return_value = juego, autospec = True)
    mocker.patch("endpoints.game.check_turno", return_value = True, autospec = True)
    mocker.patch("endpoints.game.check_carta_habilitada", return_value=None, autospec=True,)
    mocker.patch("endpoints.game.Juego.mensaje_personal", return_value = None, autospec = True)
    mocker.patch("endpoints.game.Juego.crear_intercambio", return_value=None,
                 autospec=True,)
    mocker.patch("models.player.JugadorPartida.check_puede_anular_el_intercambio", return_value=True,autospec=True,)

    response = client.post("game/play/swap_request_no_podemos_ser_amigos", data={"match_id": 1, "card_id": 10,
                            "player_orig": jugador_solicitante.id, "player_obj": jugador_solicitado.id})
    assert response.status_code == 200
    assert response.json() == {"mensaje": "se creo la solicitud de intercambio"}



def test_no_podemos_ser_amigos_endpoint_request_400_jugador_no_en_turno(mocker, mock_juego, mock_j1, mock_j2):
    jugador_solicitante: JugadorPartida = mock_j1
    jugador_solicitado: JugadorPartida = mock_j2
    mocker.patch("endpoints.game.get_global_juego", return_value=mock_juego,
                 autospec=True,)
    mocker.patch("endpoints.game.get_jugador", return_value=mock_j1,
                 autospec=True,)
    mocker.patch("endpoints.game.check_turno", side_effect=HTTPException(
        status_code=400, detail="No es el turno del jugador"), autospec=True,)
    response = client.post("game/play/swap_request_no_podemos_ser_amigos", data={"match_id": 1, "card_id": 10,
                            "player_orig": jugador_solicitante.id, "player_obj": jugador_solicitado.id})
    assert response.status_code == 400
    assert response.json() == {"detail": "Error: No es el turno del jugador"}



def test_no_podemos_ser_amigos_endpoint_response_200_ok(mocker, mock_juego, mock_j1, mock_j2):
    jugador_solicitante: JugadorPartida = mock_j1
    jugador_solicitado: JugadorPartida = mock_j2
    mocker.patch("endpoints.game.get_global_juego", return_value = mock_juego, autospec = True)
    mocker.patch("endpoints.game.check_turno", return_value = True, autospec = True)
    mocker.patch("endpoints.game.check_carta_habilitada", return_value=None, autospec=True,)
    mocker.patch("endpoints.game.Juego.mensaje_personal", return_value=None, autospec=True)
    mocker.patch("endpoints.game.Juego.responder_intercambio", return_value=None,
                 autospec=True,)
    juego.mensaje_personal(jugador_solicitado, "D")
    juego.mensaje_personal(jugador_solicitante.id, "D")
    mocker.patch("endpoints.game.check_ganador", return_value = None, autospec = True)
    mocker.patch("endpoints.game.mostrar_cartas_cuarentena", return_value=None,
                 autospec=True,)
    mocker.patch("endpoints.game.Juego.get_jugador_en_turno",
                 return_value=jugador_solicitante, autospec=True,)
    response = client.post("game/play/swap_response_no_podemos_ser_amigos", data={"match_id": 1,
                                                        "card_id": 2,
                                                        "player_orig": 2,
                                                        "se_defiende": False})
    assert response.status_code == 200
    assert response.json() == {"message": "se completo el intercambio"}
