
from fastapi import HTTPException
from logic.action_effects import play_lanzallamas
from models.game import Juego
from models.database_utils import get_jugadores_match
from models.crud import get_name


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


def check_ganador(juego: Juego) -> bool:
    first = check_la_cosa_eliminada(juego)
    second = check_no_humanos(juego)
    result = first or second
    return result


def finalizar_juego(juego: Juego):
    la_cosa = []
    humanos = []
    infectados = []
    for j in juego.jugadores_en_partida:
        name = get_name(j.id)
        if j.get_la_cosa():
            la_cosa.append(name)
        if j.get_infectado():
            infectados.append(name)
        if j.get_humano():
            humanos.append(name)

    if check_la_cosa_eliminada(juego):
        return {'message': 'Ganan los Humanos', 'winners': humanos, 'losers': la_cosa+infectados}
    elif check_no_humanos_no_eliminados(juego):
        return {'message': 'Gana La Cosa', 'winners': la_cosa, 'losers': infectados+humanos}
    elif check_no_humanos(juego):
        return {'message': 'Ganan La Cosa y Los Infectados', 'winners': la_cosa+infectados, 'losers': humanos}
    else:
        raise HTTPException(
            status_code=400, detail="No hay ganadores.")


def check_la_cosa_eliminada(juego: Juego) -> bool:
    la_cosa_eliminada = True
    for j in juego.jugadores_en_partida:
        if j.get_la_cosa() and not j.get_muerto():
            la_cosa_eliminada = False
    print(f'la_cosa_eliminada:{la_cosa_eliminada}')
    return la_cosa_eliminada


def check_no_humanos(juego: Juego) -> bool:
    no_humanos = True
    for j in juego.jugadores_en_partida:
        if j.get_humano() and not j.get_muerto():
            no_humanos = False
    print(f'no_humanos:{no_humanos}')
    return no_humanos


def check_no_humanos_no_eliminados(juego: Juego) -> bool:
    no_humanos = True
    no_muertos = True
    for j in juego.jugadores_en_partida:
        if j.get_humano() and not j.get_muerto():
            no_humanos = False
        if j.get_muerto():
            no_muertos = False
    print(f'no_humanos_no_eliminados:{no_humanos and no_muertos}')
    return no_humanos and no_muertos


def jugar_la_carta(
        juego: Juego,
        card_id: int,
        player_objective: int,
        player_orig: int):
    if card_id in [22, 23, 24, 25, 26]:
        play_lanzallamas(player_orig, player_objective, juego)
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
