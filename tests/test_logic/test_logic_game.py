import random
import pytest
from models.game import Juego
from models.player import JugadorPartida
from logic.deck import deck_es_carta_alejate
from unittest.mock import Mock, patch
from typing import List


import pytest
from fastapi.testclient import TestClient
from pony.orm import *
from models.database_utils import *
from models.crud import *


from main import app

client = TestClient(app)

mocker = Mock()


@pytest.fixture
def mock_j1(mocker):
    mocker.patch("models.player.get_name", return_value="pepe")
    mocker.patch("models.player.get_id_avatar", return_value=1)
    jugador = JugadorPartida(id=1)
    return jugador


@pytest.fixture
def mock_j2(mocker):
    mocker.patch("models.player.get_name", return_value="pedro")
    mocker.patch("models.player.get_id_avatar", return_value=1)
    jugador = JugadorPartida(id=2)
    return jugador


@pytest.fixture
def mock_j3(mocker):
    mocker.patch("models.player.get_name", return_value="jose")
    mocker.patch("models.player.get_id_avatar", return_value=1)
    jugador = JugadorPartida(id=3)
    return jugador


@pytest.fixture
def mock_j4(mocker):
    mocker.patch("models.player.get_name", return_value="juanito")
    mocker.patch("models.player.get_id_avatar", return_value=1)
    jugador = JugadorPartida(id=4)
    return jugador


def test_repartir_cartas_4_jugadores_tienen_4_cartas_ok(
        mocker, mock_j1, mock_j2, mock_j3, mock_j4):
    mazo: List[int] = {22, 23, 24, 25, 26, 27, 28,
                       29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 1}
    juego = Juego(1, 4, 2, [1, 2, 3, 4])
    juego.jugadores_en_partida = [mock_j1, mock_j2, mock_j3, mock_j4]
    juego.mazo = mazo
    juego.repartir_cartas(4)
    for jugador in juego.jugadores_en_partida:
        assert len(jugador.cartas) == 4


def test_repartir_cartas_4_cartas_uno_es_la_cosa_ok(mock_j1, mock_j2, mock_j3, mock_j4):
    mazo: List[int] = [22, 23, 24, 25, 26, 27, 28,
                       29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 1]
    juego = Juego(1, 4, 2, [1, 2, 3, 4])
    juego.jugadores_en_partida = [mock_j1, mock_j2, mock_j3, mock_j4]
    juego.mazo = mazo
    juego.repartir_cartas(4)
    count_cosa = 0
    for jugador in juego.jugadores_en_partida:
        if jugador.la_cosa:
            count_cosa += 1
            assert len(jugador.cartas) == 4
    assert count_cosa == 1

# Asignar correctamente las cartas a los jugadores


def test_repartir_cartas_asignar_cartas_del_mazo_ok(
        mocker, mock_j1, mock_j2, mock_j3, mock_j4):
    mazo = [22, 23, 24, 25, 26, 27, 28, 29, 30,
            31, 32, 33, 34, 35, 36, 37, 38, 39, 1]
    mazoCopy = [22, 23, 24, 25, 26, 27, 28, 29,
                30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 1]
    juego = Juego(1, 4, 2, [1, 2, 3, 4])
    juego.jugadores_en_partida = [mock_j1, mock_j2, mock_j3, mock_j4]
    juego.mazo = mazo
    juego.repartir_cartas(4)
    for jugador in juego.jugadores_en_partida:
        for carta in jugador.cartas:
            assert carta in mazoCopy


def test_repartir_cartas_no_se_repiten_cartas_ok(
        mocker, mock_j1, mock_j2, mock_j3, mock_j4):
    mazo: List[int] = {22, 23, 24, 25, 26, 27, 28,
                       29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 1}
    juego = Juego(1, 4, 2, [1, 2, 3, 4])
    juego.jugadores_en_partida = [mock_j1, mock_j2, mock_j3, mock_j4]
    juego.mazo = mazo
    juego.repartir_cartas(4)
    for i in range(0, 3):
        jugadorI = juego.jugadores_en_partida[i]
        for j in range(i + 1, 4):
            jugadorJ = juego.jugadores_en_partida[j]
            for k in range(0, 4):
                cartaI = jugadorI.cartas[k]
                cartaJ = jugadorJ.cartas[k]
                distintas = cartaI != cartaJ
                assert distintas

# Actualizar el mazo del juego después de repartir las cartas


def test_repartir_cartas_no_quedan_en_el_mazo_ok(
        mock_j1, mock_j2, mock_j3, mock_j4):
    mazo = [22, 23, 24, 25, 26, 27, 28, 29, 30,
            31, 32, 33, 34, 35, 36, 37, 38, 39, 1]
    juego = Juego(1, 4, 2, [1, 2, 3, 4])
    juego.jugadores_en_partida = [mock_j1, mock_j2, mock_j3, mock_j4]
    juego.mazo = mazo
    juego.repartir_cartas(4)
    for jugador in juego.jugadores_en_partida:
        for carta in jugador.cartas:
            assert carta not in juego.mazo


def test_repartir_cartas_se_hace_en_orden_aleatorio_ok(
        mocker, mock_j1, mock_j2, mock_j3, mock_j4):
    mazo = [1, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]
    mocker.patch('random.randint', return_value=0)
    juego = Juego(1, 4, 2, [1, 2, 3, 4])
    juego.jugadores_en_partida = [mock_j1, mock_j2, mock_j3, mock_j4]
    juego.mazo = mazo
    juego.repartir_cartas(4)
    assert mock_j1.cartas == [1, 25, 29, 33]
    assert mock_j2.cartas == [22, 26, 30, 34]
    assert mock_j3.cartas == [23, 27, 31, 35]
    assert mock_j4.cartas == [24, 28, 32, 36]


def test_robar_carta_determinacion_sin_cartas_de_panico_ok(mocker, mock_j1, mock_j2, mock_j3, mock_j4):
    mazo = [1, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]
    juego = Juego(1, 4, 2, [1, 2, 3, 4])
    juego.jugadores_en_partida = [mock_j1, mock_j2, mock_j3, mock_j4]
    juego.mazo = mazo
    cartas_robadas = juego.robar_carta_determinacion()
    assert (cartas_robadas == [{"id": 36}, {"id": 35}, {"id": 34}])
    assert (juego.cartas_determinacion == [36, 35, 34])


def test_robar_carta_determinacion_con_cartas_de_panico_ok(mocker, mock_j1, mock_j2, mock_j3, mock_j4):
    mazo = [1, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
            32, 33, 34, 100, 102, 35, 91, 92, 90, 36, 103]
    juego = Juego(1, 4, 2, [1, 2, 3, 4])
    juego.jugadores_en_partida = [mock_j1, mock_j2, mock_j3, mock_j4]
    juego.mazo = mazo
    cartas_robadas = juego.robar_carta_determinacion()
    assert (cartas_robadas == [{"id": 36}, {"id": 35}, {"id": 34}])
    assert (juego.cartas_determinacion == [36, 35, 34])


def test_robar_carta_determinacion_se_acaba_mazo_ok(mocker, mock_j1, mock_j2, mock_j3, mock_j4):
    mazo = [35, 36]
    juego = Juego(1, 4, 2, [1, 2, 3, 4])
    juego.jugadores_en_partida = [mock_j1, mock_j2, mock_j3, mock_j4]
    juego.mazo = mazo
    juego.mazo_descarte = [2, 3, 4, 5]
    mocker.patch('random.shuffle', return_value=[2, 3, 4, 5])
    cartas_robadas = juego.robar_carta_determinacion()
    assert (cartas_robadas == [{"id": 36}, {"id": 35}, {"id": 5}])
    assert (juego.cartas_determinacion == [36, 35, 5])
