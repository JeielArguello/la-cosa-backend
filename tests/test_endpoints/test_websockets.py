from fastapi.testclient import TestClient
from unittest.mock import Mock
from main import app
from endpoints.websocket import *

pytest_plugins = ('pytest_asyncio',)

client = TestClient(app)

mocker = Mock()


def test_websocket_listar_partidas_connect():
    client = TestClient(app)
    with client.websocket_connect("ws/match/list") as websocket:
        data = websocket.receive_json()
        assert data == {'message': 'Usuario viendo lista de partida'}
