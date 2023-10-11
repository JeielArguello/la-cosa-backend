import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from models.database import Jugador, Partida
from pony.orm import *
from models.database_utils import *
from models.crud import *
from logic.game import Juego

from main import app

client = TestClient(app)

mocker = Mock()


def test_create_match_success(mocker):
    mocker.patch("endpoints.match.validar_partida",
                 return_value=True, autospec=True,)
    mocker.patch("endpoints.match.crear_partida", return_value={
                 "id_partida": 1}, autospec=True,)

    response = client.post("/match/create", data={"id_usuario_creador": 1,
                                                  "id_name": "sala 1",
                                                  "contraseña": "1234",
                                                  "num_max_jugadores": 11,
                                                  "num_min_jugadores": 4})

    assert response.status_code == 200
    assert response.json() == {"id_partida": 1}


@pytest.fixture
def mock_partida():
    mock_partida_dict = {"id_usuario_creador": 1,
                         "id_name": "sala 1",
                         "contraseña": "1234",
                         "num_max_jugadores": 100,
                         "num_min_jugadores": 4}
    return mock_partida_dict


def test_create_match_fail(mocker, mock_partida: dict[str, any]):
    # Test: No se encontro el usuario
    mocker.patch("endpoints.match.validar_partida",
                 side_effect=ValueError("usuario no existe."), autospec=True,)

    response = client.post("/match/create", data=mock_partida)

    assert response.status_code == 400
    assert response.json() == {"detail": "Error: usuario no existe."}


def test_create_match_fail_2(mocker, mock_partida: dict[str, any]):
    # Test: El usuario esta dentro de otra partida
    mocker.patch("endpoints.match.validar_partida", side_effect=ValueError(
        "Usuario ya ingresado en una partida."), autospec=True,)
    response = client.post("/match/create", data=mock_partida)

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Error: Usuario ya ingresado en una partida."}


def test_create_match_fail_3(mocker, mock_partida: dict[str, any]):
    # Test: La partida no se pudo crear
    mocker.patch("endpoints.match.validar_partida",
                 return_value=None, autospec=True,)
    mocker.patch(
        "endpoints.match.crear_partida",
        side_effect=HTTPException(
            status_code=400,
            detail="No se pudo inicializar la partida en base de datos."),
        autospec=True,
    )
    response = client.post("/match/create", data=mock_partida)

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Error: No se pudo inicializar la partida en base de datos."}


'''
def test_join_match_success(mocker):
    mocker.patch("endpoints.match.validar_entrada_partida",
                 return_value=None, autospec=True,)
    mocker.patch("endpoints.match.update_add_player",
                 return_value=None, autospec=True,)

    response = client.post("/match/join", data={"match_id": 2, "user_id": 1})

    assert response.status_code == 200
'''


# def test_iniciar_partida_success(mocker):
#     mocker.patch("endpoints.match.database_utils_iniciar_partida",
#                  return_value=None, autospec=True)

#     response = client.post("/match/start", data={"user_id": 1, "match_id": 1})

#     assert(response.status_code == 200)
#     assert(response.json() == {"message": "Se inició con éxito la partida."})


def test_iniciar_partida_fail(mocker):
    mocker.patch(
        "endpoints.match.database_utils_iniciar_partida",
        side_effect=HTTPException(
            status_code=400,
            detail="La partida ya esta inicializada."),
        autospec=True)

    response = client.post("/match/start", data={"user_id": 1, "match_id": 1})

    assert(response.status_code == 400)
    assert(response.json() == {"detail": "La partida ya esta inicializada."})


def test_get_state_succes(mocker):
    mock_partida = {
        'iniciada': True,
        'nombre_partida': 'partida_test',
        'minimo': 4,
        'maximo': 12,
        'cantidad_jugadores': 4}
    mocker.patch('endpoints.match.get_estado_partida',
                 return_value=mock_partida, autospec=True)
    response = client.get('/match/state/1')
    assert response.status_code == 200
    assert response.json() == mock_partida


def test_get_state_fail(mocker):
    mocker.patch(
        'endpoints.match.get_estado_partida',
        side_effect=HTTPException(
            status_code=400,
            detail="La partida no existe"),
        autospec=True)
    response = client.get('/match/state/1')
    assert response.status_code == 400
    assert response.json() == {'detail': 'Error: La partida no existe'}


def test_get_game_state_succes(mocker):
    mock_juego = Juego(partida_id=1, cantidad_jugadores=2,
                       creador=1, jugadores_id=[1, 2])

    mock_status_game = {'posiciones': mock_juego.posiciones, 'jugadores': [
        {'id': 1, 'nombre': 'pepito'}, {'id': 2, 'nombre': 'jose'}], 'sentido': mock_juego.sentido}
    mocker.patch('endpoints.match.get_global_juego',
                 return_value=mock_juego, autospec=True)
    mocker.patch('endpoints.match.get_status_game',
                 return_value=mock_status_game, autospec=True)

    response = client.get('/match/game/state/1')
    assert response.status_code == 200
    assert response.json() == mock_status_game


def test_get_game_state_fail_game_no_exist(mocker):
    mocker.patch(
        'endpoints.match.get_global_juego',
        side_effect=HTTPException(
            status_code=400,
            detail="No se pudo acceder al juego"),
        autospec=True)
    response = client.get('/match/game/state/1')
    assert response.status_code == 400
    assert response.json() == {'detail': 'Error: No se pudo acceder al juego'}
