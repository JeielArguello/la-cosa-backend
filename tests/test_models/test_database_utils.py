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

def test_validar_partida(mocker):
    mocker.patch("models.database_utils.get_exist_user",return_value= True,autospec=True,)
    mocker.patch("models.database_utils.get_exist_user_in_game",return_value= False,autospec=True,)
  
    assert validar_partida(1, 12, 4) == None

def test_validar_partida_fail(mocker):
    mocker.patch("models.database_utils.get_exist_user",return_value=True,autospec=True,)
    mocker.patch("models.database_utils.get_exist_user_in_game",return_value= False,autospec=True,)
    with pytest.raises(ValueError) as excinfo:
        validar_partida(1, 14, 4)

    # Verifica que la excepción tenga el mensaje esperado
    assert str(excinfo.value) == "Numero maximo de jugadores mayor a 11."
    
def test_validar_partida_fail_2(mocker):
    mocker.patch("models.database_utils.get_exist_user",return_value=True,autospec=True,)
    mocker.patch("models.database_utils.get_exist_user_in_game",return_value= False,autospec=True,)
    with pytest.raises(ValueError) as excinfo:
        validar_partida(1, 11, 2)

    # Verifica que la excepción tenga el mensaje esperado
    assert str(excinfo.value) == "Numero minimo de jugadores menor a 4."
