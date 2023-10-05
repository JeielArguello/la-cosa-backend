import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock, MagicMock
from models.database import Jugador, Partida
from pony.orm import *
from models.database_utils import *
from models.crud import *

from main import app
client = TestClient(app)

mocker = Mock()

jugador_simulado = MagicMock()
jugador_simulado.id = 1
jugador_simulado.nombre = "Jugador1"

jugador_simulado2 = MagicMock()
jugador_simulado2.id = 2
jugador_simulado2.nombre = "Jugador2"

partida_simulada = MagicMock()
partida_simulada.id = 1

partida_simulada2 = None


set_juga_simulado  = {jugador_simulado}
set_juga_simulado2 = {jugador_simulado2, jugador_simulado}
jugadores_vacios = {}

def test_finalizar_partida(mocker):
    mocker.patch("models.database_utils.get_jugadores_en_juego",
                  return_value=set_juga_simulado, autoespec = True,)
    assert finalizar_partida(partida_simulada) == {"mensaje": "La partida ha finalizado", "ganador": 1}

def test_finalizar_partida1(mocker):   
    mocker.patch("models.database_utils.get_jugadores_en_juego",
                  return_value=set_juga_simulado2, autoespec = True,)
    assert finalizar_partida(partida_simulada) == {"mensaje": "La partida aún no ha finalizado"}


def test_finalizar_partida_fail(mocker):
    mocker.patch("models.database_utils.get_jugadores_en_juego",
                  return_value=jugadores_vacios, autoespec = True,)
    assert finalizar_partida(partida_simulada) == {"mensaje": "partida sin jugadores"}

def test_finalizar_partida_fail2(mocker):
    mocker.patch("models.database_utils.get_jugadores_en_juego",
                  return_value=None, autoespec = True,)
    with pytest.raises(AssertionError):
        finalizar_partida(partida_simulada2)
