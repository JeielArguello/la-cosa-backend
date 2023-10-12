
from fastapi import HTTPException
from models.game import Juego
from models.database_utils import get_jugadores_match


global_juegos: list[Juego] = []



def get_status_game(juego: Juego):
    posiciones = juego.posiciones
    sentido = juego.sentido
    jugadores = get_jugadores_match(juego.partida_id)
    response = {'posiciones': posiciones,
                'jugadores': jugadores, 'sentido': sentido}
    return response


def get_global_juego(match_id: int) -> Juego:
    result = None
    for juego in global_juegos:
        if juego.partida_id == match_id:
            result = juego
    if(result is None):
        raise HTTPException(
            status_code=400, detail="No se pudo acceder al juego")
    return result


def get_status_player(juego: Juego, player_id: int):
    jugador = None
    for j in juego.jugadores_en_partida:
        if j.id == player_id:
            jugador = j
    if jugador is None:
        raise HTTPException(
            status_code=400,
            detail="El jugador no se encuentra en la partida")
    mano = jugador.cartas
    muerto = jugador.muerto
    la_cosa = jugador.la_cosa
    humano = jugador.humano
    infectado = jugador.infectado
    response = {'mano': mano, 'muerto': muerto, 'la_cosa': la_cosa,
                'humano': humano, 'infectado': infectado}
    return response
