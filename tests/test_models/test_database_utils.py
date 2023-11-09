import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock, MagicMock
from models.database import Jugador, Partida
from pony.orm import *
from models.database_utils import *
from models.crud import *

from main import app
from utils.match_utils import validar_partida

client = TestClient(app)

mocker = Mock()


def test_validar_partida_ok(mocker):
    mocker.patch("utils.match_utils.get_exist_user",
                 return_value=True, autospec=True,)
    mocker.patch("utils.match_utils.get_exist_user_in_game",
                 return_value=False, autospec=True,)
    assert validar_partida(1, 12, 4) is None


def test_validar_partida_value_error_maximo_jugadores_mayor_12(mocker):
    mocker.patch("utils.match_utils.get_exist_user",
                 return_value=True, autospec=True,)
    mocker.patch("utils.match_utils.get_exist_user_in_game",
                 return_value=False, autospec=True,)
    with pytest.raises(ValueError) as excinfo:
        validar_partida(1, 14, 4)

    # Verifica que la excepción tenga el mensaje esperado
    assert str(excinfo.value) == "Numero maximo de jugadores mayor a 12."


def test_validar_partida_value_error_minimo_jugadores_menor_4(mocker):
    mocker.patch("utils.match_utils.get_exist_user",
                 return_value=True, autospec=True,)
    mocker.patch("utils.match_utils.get_exist_user_in_game",
                 return_value=False, autospec=True,)
    with pytest.raises(ValueError) as excinfo:
        validar_partida(1, 11, 2)

    # Verifica que la excepción tenga el mensaje esperado
    assert str(excinfo.value) == "Numero minimo de jugadores menor a 4."


jugador_simulado = MagicMock()
jugador_simulado.id = 1
jugador_simulado.nombre = "Jugador1"

jugador_simulado2 = MagicMock()
jugador_simulado2.id = 2
jugador_simulado2.nombre = "Jugador2"

partida_simulada = MagicMock()
partida_simulada.id = 1

partida_simulada2 = None

set_juga_simulado = {jugador_simulado}
set_juga_simulado2 = {jugador_simulado2, jugador_simulado}
jugadores_vacios = {}


# def test_finalizar_partida(mocker):
#     mocker.patch("models.database_utils.get_jugadores_en_juego",
#                  return_value=set_juga_simulado, autoespec=True,)
#     assert finalizar_partida(partida_simulada) == {
#         "mensaje": "La partida ha finalizado", "ganador": 1}


# def test_finalizar_partida1(mocker):
#     mocker.patch("models.database_utils.get_jugadores_en_juego",
#                  return_value=set_juga_simulado2, autoespec=True,)
#     assert finalizar_partida(partida_simulada) == {
#         "mensaje": "La partida aún no ha finalizado"}


# def test_finalizar_partida_fail(mocker):
#     mocker.patch("models.database_utils.get_jugadores_en_juego",
#                  return_value=jugadores_vacios, autoespec=True,)
#     assert finalizar_partida(partida_simulada) == {
#         "mensaje": "partida sin jugadores"}


# def test_finalizar_partida_fail2(mocker):
#     mocker.patch("models.database_utils.get_jugadores_en_juego",
#                  return_value=None, autoespec=True,)
#     with pytest.raises(AssertionError):
#         finalizar_partida(partida_simulada2)


def test_construir_mazo_ok(mocker):
    mocker.patch("models.database_utils.select",
                 return_value=[1, 2, 3, 4, 5, 6])
    resultado = construir_mazo(5)
    assert resultado == [1, 2, 3, 4, 5, 6]

# revisar mensaje error


def test_construir_mazo_error_numero_incorrecto_de_participantes(mocker):
    resultado = construir_mazo(15)
    assert resultado == {"error":
                         "numero de jugadores incorrecto"
                         }


def test_construir_mazo_exception_error_al_contruir_mazo(mocker):
    mocker.patch("models.database_utils.select",
                 return_value=None)
    resultado = construir_mazo(5)
    assert resultado == {"error al construir el mazo"}
