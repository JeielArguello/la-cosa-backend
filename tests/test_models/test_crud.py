import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from models.database import Jugador, Partida
from pony.orm import *
from models.database_utils import *
from models.crud import *

from main import app

client = TestClient(app)

mocker = Mock()


def test_crear_partida_ok(mocker):
    partida_mock = Mock(spec=Partida)
    jugador_mock = Mock(spec=Jugador)
    jugador_mock.id = 1
    jugador_mock.nombre = "pepe"
    mocker.patch(
        "models.crud.Jugador.get",
        return_value=jugador_mock,
        autospec=True,
    )
    partida_mock.id = 1
    partida_mock.nombre = "Partida de prueba"
    partida_mock.iniciado = False
    partida_mock.id_jugador_creador = 123
    partida_mock.minimo_jugadores = 4
    partida_mock.maximo_jugadores = 12
    partida_mock.contrasena = None
    partida_mock.jugadores = set()
    mocker.patch(
        "models.crud.Partida",
        return_value=partida_mock,
        autospec=True,
    )
    new_match = crear_partida(1, "Partida de prueba", None, 12, 4)
    assert new_match == {"id_partida": 1}
