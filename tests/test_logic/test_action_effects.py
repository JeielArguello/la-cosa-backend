from fastapi.testclient import TestClient
from unittest.mock import Mock

import pytest
from models.game import Juego
from logic.action_effects import *


from main import app
from models.player import JugadorPartida

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
def mock_atacante(mocker):
    mocker.patch("models.player.get_name", return_value="pepe")
    jugador = JugadorPartida(id=1)
    return jugador


@pytest.fixture
def mock_jugador_extra1(mocker):
    mocker.patch("models.player.get_name", return_value="pepe")
    jugador = JugadorPartida(id=3)
    return jugador


@pytest.fixture
def mock_jugador_extra2(mocker):
    mocker.patch("models.player.get_name", return_value="pepe")
    jugador = JugadorPartida(id=4)
    return jugador


@pytest.fixture
def mock_objetivo(mocker):
    mocker.patch("models.player.get_name", return_value="pedro")
    jugador = JugadorPartida(id=2)
    return jugador


def test_lanzallamas_simple(mocker, mock_juego, mock_atacante, mock_objetivo):
    mock_juego.cantidad_jugadores = 2,
    mock_juego.jugadores_id = [1, 2]
    mock_juego.posiciones = [1, 0, 2, 0]
    mock_juego.jugadores_en_partida = [mock_atacante, mock_objetivo]
    play_lanzallamas(mock_atacante.id, mock_objetivo.id, mock_juego)
    response = {'jugadores': len(mock_juego.jugadores_en_partida),
                'posiciones': mock_juego.posiciones}
    assert response == {'jugadores': 2, 'posiciones': [1, 0]}


def test_lanzallamas_varios_ataques_en_todos_sentidos(mocker, mock_juego, mock_atacante, mock_objetivo):
    mock_j1 = mock_atacante
    mock_j2 = mock_objetivo
    mock_j3 = mock_atacante
    mock_j3.id = 3
    mock_j4 = mock_atacante
    mock_j4.id = 4
    mock_j5 = mock_atacante
    mock_j5.id = 5
    mock_j6 = mock_atacante
    mock_j6.id = 6
    mock_j7 = mock_atacante
    mock_j7.id = 7
    mock_j8 = mock_atacante
    mock_j8.id = 8
    mock_j9 = mock_atacante
    mock_j9.id = 9
    mock_j10 = mock_atacante
    mock_j10.id = 10
    mock_juego.cantidad_jugadores = 10,
    mock_juego.jugadores_id = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    mock_juego.jugadores_en_partida = [
        mock_j1,
        mock_j2,
        mock_j3,
        mock_j4,
        mock_j5,
        mock_j6,
        mock_j7,
        mock_j8,
        mock_j9,
        mock_j10]
    mock_juego.posiciones = [
        1,
        0,
        2,
        0,
        3,
        0,
        4,
        0,
        5,
        0,
        6,
        0,
        7,
        0,
        8,
        0,
        9,
        0,
        10,
        0]
    mocker.patch("logic.action_effects.Juego.get_jugador", side_effect={mock_j4,mock_j5})
    mocker.patch("utils.action_utils.Juego.get_jugador", return_value=mock_j4)
    
    play_lanzallamas(4, 5, mock_juego)
    response1 = {'jugadores': len(mock_juego.jugadores_en_partida),
                 'posiciones': mock_juego.posiciones}
    assert response1 == {
        'jugadores': 10,
        'posiciones': [
            1,
            0,
            2,
            0,
            3,
            0,
            4,
            0,
            6,
            0,
            7,
            0,
            8,
            0,
            9,
            0,
            10,
            0]}
    play_lanzallamas(9, 8, mock_juego)
    response2 = {'jugadores': len(mock_juego.jugadores_en_partida),
                 'posiciones': mock_juego.posiciones}
    assert response2 == {'jugadores': 10, 'posiciones': [
        1, 0, 2, 0, 3, 0, 4, 0, 6, 0, 7, 0, 9, 0, 10, 0]}
    play_lanzallamas(10, 1, mock_juego)
    response3 = {'jugadores': len(mock_juego.jugadores_en_partida),
                 'posiciones': mock_juego.posiciones}
    assert response3 == {
        'jugadores': 10, 'posiciones': [
            2, 0, 3, 0, 4, 0, 6, 0, 7, 0, 9, 0, 10, 0]}
    play_lanzallamas(2, 10, mock_juego)
    response4 = {'jugadores': len(mock_juego.jugadores_en_partida),
                 'posiciones': mock_juego.posiciones}
    assert response4 == {'jugadores': 10,
                         'posiciones': [2, 0, 3, 0, 4, 0, 6, 0, 7, 0, 9, 0]}


def test_lanzallamas_http_exception_no_vecinos(
        mocker,
        mock_juego,
        mock_atacante,
        mock_objetivo):
    mock_juego.posiciones = [1, 0, 3, 0, 2, 0, 4, 0]
    try:
        play_lanzallamas(mock_atacante.id, mock_objetivo.id, mock_juego)
    except HTTPException as e:
        error_msg = {e.detail}
    assert error_msg == {"Los jugadores no son vecinos"}


def test_vigila_tus_espaldas_ok(mocker, mock_juego):
    mock_juego.cantidad_jugadores = 2
    mock_juego.jugadores_id = [1, 2]
    antes_cambio = mock_juego.sentido
    play_vigila_tus_espaldas(mock_juego)
    despues_cambio = mock_juego.sentido
    assert antes_cambio == despues_cambio * (-1)



def test_hacha_ok(mocker, mock_juego):
    mock_juego.cantidad_jugadores = 2
    mock_juego.jugadores_id = [1, 2]
    mock_juego.posiciones = [1, "p", 2, 0]
    play_hacha(1, 2, mock_juego)
    assert mock_juego.posiciones == [1, 0, 2, 0]


def test_hacha_http_exception_no_vecinos(mocker, mock_juego, mock_atacante, mock_objetivo):

    mock_juego.cantidad_jugadores = 4,
    mock_juego.jugadores_id = [1, 3, 2, 4]
    mock_juego.posiciones = [1, 0, 3, 0, 2, 0, 4, 0]
    try:
        play_hacha(mock_atacante.id, mock_objetivo.id, mock_juego)
    except HTTPException as e:
        error_msg = {e.detail}
    assert error_msg == {"Los jugadores no son vecinos"}


def test_hacha_http_exception_no_hay_puerta(mocker, mock_juego):
    mock_atacante = 1
    mock_objetivo = 2
    mock_juego.cantidad_jugadores = 4,
    mock_juego.jugadores_id = [1, 2, 3, 4]
    try:
        play_hacha(mock_atacante, mock_objetivo, mock_juego)
    except HTTPException as e:
        error_msg = {e.detail}
    assert error_msg == {"No hay una puerta atrancada"}


def test_mas_vale_que_corras_ok(mock_juego, mock_atacante, mock_objetivo):
    play_mas_vale_que_corras(mock_atacante.id, mock_objetivo.id, mock_juego)
    response = {'jugadores': len(mock_juego.jugadores_en_partida),
                'posiciones': mock_juego.posiciones}
    assert response == {'jugadores': 4, 'posiciones': [2, 0, 1, 0, 3, 0, 4, 0]}


def test_sospecha_ok(mocker, mock_juego, mock_atacante, mock_objetivo):
    mock_juego.jugadores_en_partida = [mock_atacante, mock_objetivo]
    mock_objetivo.cartas = [1, 2, 3, 4]
    mocker.patch(
        "logic.action_effects.get_name_carta",
        return_value="sospecha")
    msg = play_sospecha(mock_atacante.id, mock_objetivo.id, mock_juego)
    assert msg["mensaje"] == "pepe jugó carta sospecha contra pedro"
    assert msg["cartaMostrar"][0] in [
        {"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}]

# revisar mensaje error


def test_sospecha_http_exception_no_se_puede_obtener_carta(mock_juego, mocker):
    mock_atacante = 1
    mock_objetivo = 2
    mocker.patch("logic.action_effects.random.choice", return_value=4)
    mocker.patch(
        "logic.action_effects.get_name_carta",
        return_value="sospecha")
    try:
        play_sospecha(mock_atacante, mock_objetivo, mock_juego)
    except HTTPException as e:
        error_msg = {e.detail}
    assert error_msg == {"No se pudo obtener una carta del jugador objetivo"}


def test_cambio_de_lugar_ok_2_jugadores(
        mocker, mock_juego, mock_atacante, mock_objetivo):
    j1 = mock_atacante
    j2 = mock_objetivo
    mock_juego.posiciones = [1, 0, 2, 0]
    mock_juego.jugadores_en_partida = [j1, j2]
    mock_juego.jugadores_id = [1, 2]
    j1.posicion = 0
    j2.posicion = 2
    play_cambio_de_lugar(mock_juego, j1.id, j2.id)
    assert (j1.posicion == 2)
    assert (j2.posicion == 0)
    assert (mock_juego.posiciones == [2, 0, 1, 0])


def test_cambio_de_lugar_ok_4_jugadores(
        mocker,
        mock_juego,
        mock_atacante,
        mock_objetivo,
        mock_jugador_extra1,
        mock_jugador_extra2):
    j1 = mock_atacante
    j2 = mock_objetivo
    j3 = mock_jugador_extra1
    j4 = mock_jugador_extra2
    mock_juego.jugadores_en_partida = [j1, j2, j3, j4]
    j1.posicion = 0
    j2.posicion = 2
    j3.posicion = 4
    j4.posicion = 6
    play_cambio_de_lugar(mock_juego, j1.id, j4.id)
    assert (j1.posicion == 6)
    assert (j4.posicion == 0)
    assert (mock_juego.posiciones == [4, 0, 2, 0, 3, 0, 1, 0])


def test_play_analisis_ok(mocker, mock_juego, mock_atacante, mock_objetivo):
    mock_juego.jugadores_en_partida = [mock_atacante, mock_objetivo]
    mock_juego.posiciones = [1, 0, 2, 0]
    mock_objetivo.cartas = [10, 2, 3, 4]
    msg = play_analisis(mock_juego, mock_atacante.id, mock_objetivo.id)
    assert (msg["mensaje"] == "pepe jugó carta Análisis contra pedro.")
    assert (msg["cartaMostrar"] == [
        {'id': 10}, {'id': 2}, {'id': 3}, {'id': 4}])


def test_play_whisky_ok(mocker, mock_juego, mock_atacante):
    mock_juego.jugadores_en_partida = [mock_atacante]
    mock_atacante.cartas = [1, 10, 2, 3, 4]
    mock_card_id = 1
    msg = play_whisky(mock_atacante.id, mock_juego, mock_card_id)
    assert (msg["mensaje"] == "pepe jugó carta Whisky.")
    assert (msg["cartaMostrar"] == [
        {'id': 10}, {'id': 2}, {'id': 3}, {'id': 4}])


def test_play_whisky_error_no_se_pudo_mostrar_cartas(mocker, mock_juego):
    mock_card_id = 1
    mocker.patch("logic.action_effects.get_jugador", return_value=None)
    msg = play_whisky(4000, mock_juego, mock_card_id)
    assert msg == {"error": "no se pudieron mostrar cartas."}


def test_play_seduccion_ok(mocker, mock_juego, mock_atacante, mock_objetivo):
    mock_juego.jugadores_en_partida = [mock_atacante, mock_objetivo]
    mocker.patch("logic.action_effects.is_cuarentena", return_value = False)
    msg = play_seduccion(mock_juego, mock_atacante.id, mock_objetivo.id)
    assert msg == {"mensaje": "pepe" + " jugó carta Seducción contra "
                   + "pedro" + "."}


def test_play_seduccion_error_objetivo_en_cuarentena(mocker, mock_juego, mock_atacante, mock_objetivo):
    mock_juego.jugadores_en_partida = [mock_atacante, mock_objetivo]
    mocker.patch("logic.action_effects.is_cuarentena", return_value = True)
    msg = play_seduccion(mock_juego, mock_atacante.id, mock_objetivo.id)
    assert msg == {"mensaje": "error pedro en cuarentena."}


def test_play_determinacion_ok(mocker, mock_juego, mock_atacante):
    mock_juego.jugadores_en_partida = [mock_atacante]
    mock_atacante.cartas = [1, 44, 2, 3, 4]
    mock_juego.mazo = [23, 22, 21, 4, 5, 6, 7, 8]
    msg = play_determinacion(mock_juego, mock_atacante.id)
    assert (msg["mensaje"] == "pepe jugó carta Determinación.")
    assert (msg["cartas"] == [{'id': 8}, {'id': 7}, {'id': 6}])
    assert (mock_juego.cartas_determinacion == [8, 7, 6])
