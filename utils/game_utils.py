
from fastapi import HTTPException
from logic.action_effects import play_lanzallamas, play_mas_vale_que_corras
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



def delete_global_juego(match_id):
    result = None
    for juego in global_juegos:
        if juego.partida_id == match_id:
            result = juego
    if(result is None):
        raise HTTPException(
            status_code=400, detail="No se puedo borrar el juego")
    global_juegos.remove(result)


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



def jugar_la_carta(
        juego: Juego,
        card_id: int,
        player_objective: int,
        player_orig: int):
    if card_id in [22, 23, 24, 25, 26]:
        play_lanzallamas(player_orig, player_objective, juego)
        return True
    if card_id in [55, 56, 57, 58, 59]:
        play_mas_vale_que_corras(player_orig, player_objective, juego)
        return True
    else:
        return False


def finalizar_partida(juego: Juego):
    if len(juego.jugadores_en_partida) == 1:
        ganador = juego.jugadores_en_partida.pop()
        ganador_id = ganador.id
        return {"mensaje": "La partida ha finalizado", "ganador": ganador_id}
    elif len(juego.jugadores_en_partida) == 0:
        return {"mensaje": "partida sin jugadores", "ganador": 0}
    else:
        return {"mensaje": "La partida aún no ha finalizado", "ganador": 0}


