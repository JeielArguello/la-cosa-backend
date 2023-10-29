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
    jugador = JugadorPartida(id=1)
    return jugador


@pytest.fixture
def mock_j2(mocker):
    mocker.patch("models.player.get_name", return_value="pedro")
    jugador = JugadorPartida(id=2)
    return jugador


@pytest.fixture
def mock_j3(mocker):
    mocker.patch("models.player.get_name", return_value="jose")
    jugador = JugadorPartida(id=3)
    return jugador


@pytest.fixture
def mock_j4(mocker):
    mocker.patch("models.player.get_name", return_value="juanito")
    jugador = JugadorPartida(id=4)
    return jugador


def test_repartirCartas_4jugadoresCon4Cartas(
        mocker, mock_j1, mock_j2, mock_j3, mock_j4):

    mazo: List[int] = {22, 23, 24, 25, 26, 27, 28,
                       29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 1}

    juego = Juego(1, 4, 2, [1, 2, 3, 4])
    juego.jugadores_en_partida = [mock_j1, mock_j2, mock_j3, mock_j4]
    juego.mazo = mazo
    juego.repartir_cartas(4)

    for jugador in juego.jugadores_en_partida:
        assert len(jugador.cartas) == 4


def test_repartir_4_cartas_uno_cosa(mock_j1, mock_j2, mock_j3, mock_j4):

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


def test_asignar_correctamente_cartas_a_jugadores(
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


def test_repartirCartas_diferentes_cartas_a_jugadores(
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


def test_actualizar_mazo_despues_de_repartir_cartas(
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


def test_asignar_cartas_orden_aleatorio(
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
