import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock
from endpoints.match import abandonar_partida
from endpoints.websocket import broadcast
from models.database import Jugador, Partida
from pony.orm import *
from models.database_utils import *
from models.crud import *
from models.game import Juego
from models.lobby_models import Lobby, delete_lobby


from main import app

client = TestClient(app)

mocker = Mock()


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
def mock_partida():
    mock_partida_dict = {"id_usuario_creador": 1,
                         "id_name": "sala 1",
                         "contraseña": "1234",
                         "num_max_jugadores": 100,
                         "num_min_jugadores": 4}
    return mock_partida_dict


@pytest.fixture
def mock_lobby():
    mock_lobby = Lobby(
        id_usuario_creador=1,
        id_name="sala 1",
        contraseña="1234",
        num_max_jugadores=11,
        num_min_jugadores=4,
        id_partida=1)
    return mock_lobby


def test_create_match_200_ok(mocker):
    mocker.patch("endpoints.match.validar_partida",
                 return_value=True, autospec=True,)
    mocker.patch("endpoints.match.crear_partida", return_value={
                 "id_partida": 1}, autospec=True,)
    response = client.post("/match/create", data={"id_usuario_creador": 1,
                                                  "id_name": "sala 1",
                                                  "contraseña": "1234",
                                                  "num_max_jugadores": 11,
                                                  "num_min_jugadores": 4})
    assert response.status_code != 422, "Los parametros de entrada del endpoint no pueden ser procesados"
    assert response.status_code == 200, "el resultado deberia ser 200"
    assert response.json() == {"id_partida": 1}


def test_create_match_400_usuario_no_existe(mocker, mock_partida: dict[str, any]):
    # Test: No se encontro el usuario
    mocker.patch("endpoints.match.validar_partida",
                 side_effect=ValueError("usuario no existe."), autospec=True,)
    response = client.post("/match/create", data=mock_partida)
    assert response.status_code != 422, "Los parametros de entrada del endpoint no pueden ser procesados"
    assert response.status_code == 400
    assert response.json() == {"detail": "Error: usuario no existe."}


def test_create_match_400_usuario_ya_en_partida(mocker, mock_partida: dict[str, any]):
    # Test: El usuario esta dentro de otra partida
    mocker.patch("endpoints.match.validar_partida", side_effect=ValueError(
        "Usuario ya ingresado en una partida."), autospec=True,)
    response = client.post("/match/create", data=mock_partida)
    assert response.status_code != 422, "Los parametros de entrada del endpoint no pueden ser procesados"
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Error: Usuario ya ingresado en una partida."}

# revisar mensaje de error


def test_create_match_400_no_se_pudo_crear(mocker, mock_partida: dict[str, any]):
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
    assert response.status_code != 422, "Los parametros de entrada del endpoint no pueden ser procesados"
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Error: No se pudo inicializar la partida en base de datos."}


def test_join_match_200_ok(mocker, mock_lobby: Lobby):
    mocker.patch("endpoints.match.validar_entrada_partida",
                 return_value=None, autospec=True,)
    mocker.patch("endpoints.match.update_add_player",
                 return_value=None, autospec=True,)
    estado = {
        'iniciada': 1,
        'nombre_partida': "sala 1",
        'minimo': 4,
        'maximo': 12,
        'cantidad_jugadores': 2}
    mocker.patch("endpoints.match.get_estado_partida",
                 return_value=estado, autospec=True,)
    mocker.patch("endpoints.match.get_lobby",
                 return_value=mock_lobby, autospec=True,)
    mocker.patch("endpoints.match.broadcast",
                 return_value=None, autospec=True,)
    response = client.post(
        "/match/join",
        data={
            "match_id": 2,
            "user_id": 1,
            "contrasena": "1234"})
    assert len(mock_lobby.list_players()) == 2
    assert response.status_code != 422, "Los parametros de entrada del endpoint no pueden ser procesados"
    assert response.status_code == 200, "El status_code es distinto de 200"
    assert response.json() == estado


def test_join_match_400_mal_contraseña(mocker):
    mocker.patch(
        "endpoints.match.validar_entrada_partida",
        side_effect=ValueError("Contraseña incorrecta"),
        autospec=True,
    )
    mocker.patch("endpoints.match.update_add_player",
                 return_value=None, autospec=True,)

    response = client.post(
        "/match/join",
        data={
            "match_id": 2,
            "user_id": 1,
            "contrasena": "12345"})
    assert response.status_code != 422, "Los parametros de entrada del endpoint no pueden ser procesados"
    assert response.status_code == 400, "El status_code es distinto de 400 en caso de error"
    assert response.json() == {
        "detail": "Error: Contraseña incorrecta"}, "El detalle de el error es incorrecto"


def test_join_match_400_no_usuario(mocker, mock_lobby: Lobby):
    mocker.patch("endpoints.match.validar_entrada_partida",
                 return_value=None, autospec=True,)
    mocker.patch("endpoints.match.update_add_player",
                 side_effect=HTTPException(status_code=400,
                                           detail="No se pudo obtener el usuario"),
                 autospec=True,)
    response = client.post(
        "/match/join",
        data={"match_id": 2,
              "user_id": 1,
              "contrasena": "1234"})
    assert response.status_code != 422, "Los parametros de entrada del endpoint no pueden ser procesados"
    assert response.status_code == 400
    assert response.json() == {
        'detail': 'Error: No se pudo obtener el usuario'}


def test_get_state_partida_200_ok(mocker):
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


def test_get_state_partida_400_partida_no_existe(mocker):
    mocker.patch(
        'endpoints.match.get_estado_partida',
        side_effect=HTTPException(
            status_code=400,
            detail="La partida no existe"),
        autospec=True)
    response = client.get('/match/state/1')
    assert response.status_code == 400
    assert response.json() == {'detail': 'Error: La partida no existe'}


def test_list_vacia_200_ok(mocker):
    lista_partida = []
    mocker.patch("endpoints.match.listar_partidas",
                 return_value=[], autospec=True,)
    response = client.get("/match/list")
    assert response.status_code == 200
    assert response.json() == lista_partida


def test_list_200_ok(mocker):
    lista_partida = [{
        'iniciada': 1,
        'nombre_partida': "sala 1",
        'minimo': 4,
        'maximo': 12,
        'cantidad_jugadores': 2}]
    mocker.patch("endpoints.match.listar_partidas",
                 return_value=lista_partida, autospec=True,)
    response = client.get("/match/list")
    assert response.status_code == 200
    assert response.json() == lista_partida

# revisar mensaje de error


def test_list_400_no_se_pudo_obtener_partidas(mocker):
    mocker.patch("endpoints.match.listar_partidas", side_effect=HTTPException(
        status_code=400, detail="No se pudo obtener la partida"), autospec=True,)
    response = client.get("/match/list")
    assert response.status_code == 400
    assert response.json() == {
        'detail': "Error: No se pudo obtener la partida"}


def test_get_game_state_200_ok(mocker, mock_juego):
    mock_juego.cantidad_jugadores = 2
    mock_juego.jugadores_id = [1, 2]
    mock_status_game = {'posiciones': mock_juego.posiciones, 'jugadores': [
        {'id': 1, 'nombre': 'pepito'}, {'id': 2, 'nombre': 'jose'}], 'sentido': mock_juego.sentido}
    mocker.patch('endpoints.match.get_global_juego',
                 return_value=mock_juego, autospec=True)
    mocker.patch('endpoints.match.get_status_game',
                 return_value=mock_status_game, autospec=True)
    response = client.get('/match/game/state/1')
    assert response.status_code == 200
    assert response.json() == mock_status_game


def test_get_game_state_400_game_no_exist(mocker):
    mocker.patch(
        'endpoints.match.get_global_juego',
        side_effect=HTTPException(
            status_code=400,
            detail="No se pudo acceder al juego"),
        autospec=True)
    response = client.get('/match/game/state/1')
    assert response.status_code == 400
    assert response.json() == {'detail': 'Error: No se pudo acceder al juego'}


def test_get_player_state_200_ok(mocker, mock_juego):
    mock_juego.cantidad_jugadores = 2
    mock_juego.jugadores_id = [1, 2]
    mock_status_player = {
        'mano': [{'id': 1}, {'id': 2}, {'id': 3}, {'id': 4}],
        'muerto': False,
        'la_cosa': True,
        'humano': False,
        'infectado': True}
    mocker.patch('endpoints.match.get_global_juego',
                 return_value=mock_juego, autospec=True)
    mocker.patch('endpoints.match.get_status_player',
                 return_value=mock_status_player, autospec=True)

    response = client.get('/match/player/state/1/1')
    assert response.status_code == 200
    assert response.json() == mock_status_player


def test_get_player_state_400_game_no_exist(mocker):
    mocker.patch(
        'endpoints.match.get_global_juego',
        side_effect=HTTPException(
            status_code=400,
            detail="No se pudo acceder al juego"),
        autospec=True)
    response = client.get('/match/player/state/1/1')
    assert response.status_code == 400
    assert response.json() == {'detail': 'Error: No se pudo acceder al juego'}


def test_get_player_state_400_jugador_no_esta_en_la_partida(mocker, mock_juego):
    mock_juego.cantidad_jugadores = 2
    mock_juego.jugadores_id = [1, 2]
    mocker.patch('endpoints.match.get_global_juego',
                 return_value=mock_juego, autospec=True)
    mocker.patch(
        'endpoints.match.get_status_player',
        side_effect=HTTPException(
            status_code=400,
            detail="El jugador no se encuentra en la partida"),
        autospec=True)
    response = client.get('/match/player/state/1/1')
    assert response.status_code == 400
    assert response.json() == {
        'detail': 'Error: El jugador no se encuentra en la partida'}


def test_abandonar_partida_jugador_no_creador_200_ok(mocker):
    # Crear un objeto Lobby para el mock
    mock_lobby = Lobby(
        id_usuario_creador=1,
        id_name="Sala de Prueba",
        contraseña="laContrasenas",
        num_max_jugadores=4,
        num_min_jugadores=2,
        id_partida=1
    )
    mocker.patch("endpoints.match.get_lobby", return_value=mock_lobby)
    mocker.patch(
        "endpoints.match.models_crud_eliminar_jugador_no_creador_de_pratida_sin_inicializar",
        return_value=None)
    mocker.patch("endpoints.match.Lobby.broadcast_lobby", return_value=None)
    mock_lobby.add_player(2)
    response = client.post(
        "/match/exit",
        data={
            "id_jugador": 2,
            "match_id": 1})
    assert response.status_code == 200
    # Verifica que el jugador se haya eliminado del lobby
    assert 2 not in mock_lobby.list_players()


def test_abandonar_partida_jugador_creador_200_ok(mocker):
    # Crear un objeto Lobby para el mock
    mock_lobby = Lobby(
        id_usuario_creador=1,
        id_name="Sala de Prueba",
        contraseña="laContrasenas",
        num_max_jugadores=4,
        num_min_jugadores=2,
        id_partida=1
    )
    mocker.patch("endpoints.match.get_lobby", return_value=mock_lobby)
    mocker.patch("endpoints.match.broadcast", return_value=None)
    mocker.patch("endpoints.match.delete_match", return_value=None)
    mocker.patch("endpoints.match.delete_lobby", return_value=None)
    mock_lobby.add_player(2)
    response = client.post(
        "/match/exit",
        data={
            "id_jugador": 1,
            "match_id": 1})
    assert response.status_code == 200


def test_abandonar_partida_jugador_no_creador_400_no_jugador(mocker):
    # Crear un objeto Lobby para el mock
    mock_lobby = Lobby(
        id_usuario_creador=1,
        id_name="Sala de Prueba",
        contraseña="laContrasenas",
        num_max_jugadores=4,
        num_min_jugadores=2,
        id_partida=1
    )
    mocker.patch("endpoints.match.get_lobby", return_value=mock_lobby)
    mocker.patch(
        'endpoints.match.models_crud_eliminar_jugador_no_creador_de_pratida_sin_inicializar',
        side_effect=HTTPException(
            status_code=400,
            detail="No se obtuvo el jugador."),
        autospec=True)
    response = client.post("/match/exit",
                           data={
                               "id_jugador": 2,
                               "match_id": 1})
    assert response.status_code == 400
    assert response.json() == {
        'detail': 'Error: No se obtuvo el jugador.'}


def test_iniciar_partida_200_ok(mocker, mock_lobby: Lobby):
    mocker.patch('endpoints.match.database_utils_iniciar_partida',
                 return_value=None, autospec=True)
    mocker.patch("endpoints.match.get_lobby",
                 return_value=mock_lobby, autospec=True)
    mocker.patch("endpoints.match.Lobby.init_game",
                 return_value=None, autospec=True)
    mocker.patch("endpoints.match.broadcast",
                 return_value=None, autospec=True)
    mocker.patch("endpoints.match.Lobby.broadcast_lobby",
                 return_value=None, autospec=True)
    response = client.post("/match/start", data={
        "user_id": 1,
        "match_id": 1})
    assert response.status_code == 200
    assert response.json() == {"message": "Se inició con éxito la partida."}


def test_iniciar_partida_400_ya_iniciada(mocker):
    mocker.patch(
        "endpoints.match.database_utils_iniciar_partida",
        side_effect=HTTPException(
            status_code=400,
            detail="La partida ya esta inicializada."),
        autospec=True)
    response = client.post("/match/start", data={"user_id": 1, "match_id": 1})
    assert (response.status_code == 400)
    assert (response.json() == {
            'detail': 'Error: La partida ya esta inicializada.'})


def test_iniciar_partida_400_invalid_match_id(mocker):
    mocker.patch(
        'endpoints.match.database_utils_iniciar_partida',
        side_effect=HTTPException(
            status_code=400,
            detail="El match_id no es válido"),
        autospec=True)
    response = client.post("/match/start", data={
        "user_id": 1,
        "match_id": 100})
    assert response.status_code == 400
    assert response.json() == {
        'detail': 'Error: El match_id no es válido'}
