from fastapi.testclient import TestClient
from unittest.mock import Mock
from logic.game import Juego
from logic.action_effects import play_lanzallamas


from main import app

client = TestClient(app)

mocker = Mock()


def test_lanzallamas(mocker):
    mock_atacante = 1
    mock_objetivo = 2
    mock_juego = Juego(partida_id=1, cantidad_jugadores=2,
                       creador=1, jugadores_id=[1, 2])
    play_lanzallamas(mock_atacante, mock_objetivo, mock_juego)
    response = {'jugadores': len(mock_juego.jugadores_en_partida),
                'posiciones': mock_juego.posiciones}
    assert response == {'jugadores': 1, 'posiciones': [1, 0]}
