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


def test_create_user_200_ok(mocker):
    """Test para asegurar que el endpoint /create devuelve un jugador correctamente."""
    mock_jugador = {"id": 1, "user_name": "TestUser","id_avatar":1}
    mocker.patch("endpoints.user.db_create_user",
                 return_value=mock_jugador, autospec=True,)
    response = client.post("/user/create", data={"user_name": "TestUser","id_avatar":1})
    assert response.status_code == 200
    assert response.json() == mock_jugador


def test_create_user_400_error_al_crear(mocker):
    """Test para asegurar que el endpoint /create devuelve un jugador ."""
    mocker.patch("endpoints.user.db_create_user",
                 side_effect=KeyError(), autospec=True,)
    response = client.post("/user/create", data={"user_name": "TestUser","id_avatar":1})
    assert response.status_code == 400
    assert response.json() == {"detail": "Error al crear usuario."}
