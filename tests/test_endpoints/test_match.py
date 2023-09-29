import unittest
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock ,MagicMock
from models.database import Jugador, Partida
from pony.orm import *
from models.database_utils import *
from models.crud import *


from main import app

client = TestClient(app)

mocker = Mock()

def test_create_match_success(mocker):
    mocker.patch("endpoints.match.validar_partida",return_value= True,autospec=True,)
    mocker.patch("endpoints.match.crear_partida",return_value= {"id_partida": 1},autospec=True,)
    
    response = client.post("/match/create", data={"id_usuario_creador": 1,
                       "id_name": "sala 1",
                       "contraseña": "1234",
                       "num_max_jugadores": 11,
                       "num_min_jugadores": 4 })
    
    assert response.status_code == 200
    assert response.json() == {"id_partida": 1}

def test_create_match_fail(mocker):
    mocker.patch("endpoints.match.validar_partida",return_value=True,autospec=True,)
    mocker.patch("endpoints.match.crear_partida",side_effect=KeyError(),autospec=True,)
    
    response = client.post("/match/create", data={"id_usuario_creador": 1,
                       "id_name": "sala 1",
                       "contraseña": "1234",
                       "num_max_jugadores": 100,
                       "num_min_jugadores": 4 })
    
    assert response.status_code == 400
    assert response.json() == {"detail": "Error al crear la partida."}

def test_create_user_success(mocker):
    """Test para asegurar que el endpoint /create devuelve un jugador correctamente."""
    mock_jugador = {"id": 1, "nombre": "TestUser"}
    mocker.patch("endpoints.user.db_create_user",return_value = mock_jugador,autospec=True,)

    response = client.post("/user/create", data={"usuario": "TestUser"})
    assert response.status_code == 200
    assert response.json() == mock_jugador 


def test_create_user_fail(mocker):
    """Test para asegurar que el endpoint /create devuelve un jugador ."""
    mocker.patch("endpoints.user.db_create_user",side_effect=KeyError() ,autospec=True,)

    response = client.post("/user/create", data={"usuario": "TestUser"})
    assert response.status_code == 400
    assert response.json() == {"detail":"Error al crear usuario."}

def test_validar_partida(mocker):
    mocker.patch("models.database_utils.get_exist_user",return_value= True,autospec=True,)
    mocker.patch("models.database_utils.get_exist_user_in_game",return_value= False,autospec=True,)
  
    assert validar_partida(1, 12, 4) == None

def test_validar_partida_fail(mocker):
    mocker.patch("models.database_utils.get_exist_user",return_value=False,autospec=True,)
    mocker.patch("models.database_utils.get_exist_user_in_game",return_value= False,autospec=True,)
  
    response = validar_partida(1, 12, 4) 
    assert response == HTTPException

    assert response.json() == { "detail":"Usuario no existe"} 

def test_crear_partida(mocker):
    partida_mock = Mock(spec=Partida)
    jugador_mock = Mock(spec=Jugador)

    jugador_mock.id = 1
    jugador_mock.nombre = "pepe"
    mocker.patch("models.crud.Jugador.get",return_value=jugador_mock,autospec=True,)
    
    partida_mock.id = 1
    partida_mock.nombre = "Partida de prueba"
    partida_mock.iniciado = False
    partida_mock.id_jugador_creador = 123
    partida_mock.minimo_jugadores = 4
    partida_mock.maximo_jugadores = 12
    partida_mock.contrasena = None
    partida_mock.jugadores = set()
    mocker.patch("models.crud.Partida",return_value=partida_mock,autospec=True,)

    new_match = crear_partida(1, "Partida de prueba", None,12, 4)
    assert new_match == {"id_partida": 1}