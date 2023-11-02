
from models.crud import get_name, read_carta
from models.database_utils import get_jugadores_match
from models.game import Juego
from models.player import JugadorPartida
from logic.action_effects import * 


from fastapi import HTTPException

from utils.action_utils import get_jugador


global_juegos: list[Juego] = []


def get_status_game(juego: Juego):
    posiciones = juego.posiciones
    sentido = juego.sentido
    jugadores = get_jugadores_match(juego.posiciones)
    carta = read_carta(juego.mazo[-1])
    id_player_turno = juego.get_jugador_en_turno().id
    response = {'posiciones': posiciones,
                'jugadores': jugadores,
                'sentido': sentido,
                'tipo_dorso': carta.tipo_dorso,
                'id_player_turno': id_player_turno}
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
    mano = jugador.get_cartas()
    muerto = jugador.muerto
    la_cosa = jugador.la_cosa
    humano = jugador.humano
    infectado = jugador.infectado
    response = {'mano': mano, 'muerto': muerto, 'la_cosa': la_cosa,
                'humano': humano, 'infectado': infectado}
    return response


def check_ganador(juego: Juego) -> bool:
    first = check_la_cosa_eliminada(juego)
    second = check_la_cosa_sola_viva(juego)
    third = check_no_humanos_no_eliminados(juego)
    result = first or second or third
    return result


def finalizar_juego(juego: Juego):
    la_cosa = []
    humanos_vivos = []
    humanos_muertos = []
    infectados_vivos = []
    infectados_muertos = []
    for j in juego.jugadores_en_partida:
        name = get_name(j.id)
        if j.get_la_cosa():
            la_cosa.append(name)
        if j.get_infectado() and not j.get_muerto():
            infectados_vivos.append(name)
        if j.get_infectado() and j.get_muerto():
            infectados_muertos.append(name)
        if j.get_humano() and not j.get_muerto():
            humanos_vivos.append(name)
        if j.get_humano() and j.get_muerto():
            humanos_muertos.append(name)

    if check_la_cosa_eliminada(juego):
        return {
            'message': 'La cosa fue eliminada, Ganan los Humanos.',
            'winners': humanos_vivos,
            'losers': la_cosa + infectados_vivos + infectados_muertos + humanos_muertos}
    elif check_no_humanos_no_eliminados(juego):
        return {
            'message': 'Todos fueron infectados, Gana La Cosa.',
            'winners': la_cosa,
            'losers': infectados_vivos + infectados_muertos + humanos_vivos + humanos_muertos}
    elif check_no_humanos(juego):
        return {
            'message': 'Ganan La Cosa y Los Infectados.',
            'winners': la_cosa + infectados_vivos,
            'losers': humanos_vivos + humanos_muertos + infectados_muertos}
    elif not check_no_humanos(juego):
        return {
            'message': 'La cosa decreto mal el fin de la partida, Ganan los Humanos.',
            'winners': humanos_vivos,
            'losers': la_cosa + infectados_vivos + humanos_muertos + infectados_muertos}
    elif check_la_cosa_sola_viva(juego):
        return {
            'message': 'La cosa la ultima en pie, Gana la Cosa.',
            'winners': la_cosa,
            'losers': humanos_vivos+ infectados_vivos + humanos_muertos + infectados_muertos}
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

def check_la_cosa_sola_viva(juego:Juego) -> bool:
    la_cosa_sola_viva = True
    for j in juego.jugadores_en_partida:
        if not j.get_la_cosa() and not j.get_muerto():
            la_cosa_sola_viva = False
    return la_cosa_sola_viva

async def jugar_la_carta(
        juego: Juego,
        card_id: int,
        player_objective: int,
        player_orig: int):
    validar_jugada(juego, card_id, player_objective, player_orig)
    
    if card_id in [22, 23, 24, 25, 26]:
        msg = play_lanzallamas(player_orig, player_objective, juego)
        await juego.broadcast_global({"carta_id": card_id,
                                     "mensaje":msg["mensaje"]})
        await juego.mensaje_personal(player_objective,"D")
    
    elif card_id in [27,28,29]:
        msg = play_analisis(juego,player_orig,player_objective) 
        await juego.broadcast_global({"carta_id": card_id,
                                        "mensaje": msg["mensaje"]})
        await juego.mensaje_personal(player_orig,
                                     {"carta_id":card_id,
                                      "jugador_obj": get_name(player_objective),
                                        "mensaje":msg["mensaje"],
                                        "cartaMostrar":msg["cartaMostrar"]})
    
    elif card_id in [30, 31]:
        msg = play_hacha(player_orig, player_objective, juego)
        await juego.broadcast_global({"carta_id": card_id,
                                        "mensaje": msg["mensaje"]})
        await juego.broadcast_global("C")   
    
    elif card_id in [32, 33, 34, 35, 36, 37, 38, 39]:
        msg = play_sospecha(player_orig, player_objective, juego)
        await juego.broadcast_global({"carta_id": card_id,
                                        "mensaje": msg["mensaje"]})
        await juego.mensaje_personal(player_orig,{"carta_id":card_id,
                                      "mensaje":msg["mensaje"],
                                      "cartaMostrar":msg["cartaMostrar"],
                                      "jugador_obj": get_name(player_objective)})
    
    elif card_id in [40, 41, 42]:
        msg = play_whisky(player_orig, juego, card_id)
        await juego.broadcast_global({"carta_id": card_id,
                                        "mensaje": msg["mensaje"],
                                        "cartaMostrar":msg["cartaMostrar"],
                                        "jugador_obj": get_name(player_objective)})
    
    elif card_id in [48, 49]:
        play_vigila_tus_espaldas(juego)
        name_player = get_name(player_orig)
        await juego.broadcast_global({"carta_id": card_id,
                                        "mensaje": name_player + " jugó carta vigila tus espaldas."})
        await juego.broadcast_global("C")
    
    elif card_id in [50,51,52,53,54]:
        msg = play_cambio_de_lugar(juego,player_orig,player_objective)
        await juego.broadcast_global({"carta_id": card_id,
                                        "mensaje": msg["mensaje"]})
    
    elif card_id in [55, 56, 57, 58, 59]:
        msg = play_mas_vale_que_corras(player_orig, player_objective, juego)
        await juego.broadcast_global({"carta_id": card_id,
                                        "mensaje": msg["mensaje"]})
        await juego.broadcast_global("C")

    elif card_id in [43,44,45,46,47]:
        msg = play_determinacion(juego,player_orig)
        await juego.mensaje_personal(player_orig,{
            "cartas_determinacion":msg["cartas"]
        })
        await juego.broadcast_global({
            "carta_id":card_id,
            "mensaje":msg["mensaje"]
        })
    else:
        pass


def validar_jugada(juego: Juego,
                   card_id: int,
                   player_objective: int,
                   player_orig: int):
    if player_orig not in juego.posiciones:
        raise HTTPException(
            status_code=400, detail="Atacante no esta en el juego")
    if player_objective not in juego.posiciones:
        raise HTTPException(
            status_code=400, detail="Objetivo no esta en el juego")
    for j in juego.jugadores_en_partida:
        if player_orig == j.id:
            jugador = j
    if not (card_id in jugador.cartas):
        raise HTTPException(
            status_code=400, detail="El jugador no posee esta carta")


def finalizar_partida(juego: Juego):
    if len(juego.jugadores_en_partida) == 1:
        ganador = juego.jugadores_en_partida.pop()
        ganador_id = ganador.id
        return {"mensaje": "La partida ha finalizado", "ganador": ganador_id}
    elif len(juego.jugadores_en_partida) == 0:
        return {"mensaje": "partida sin jugadores", "ganador": 0}
    else:
        return {"mensaje": "La partida aún no ha finalizado", "ganador": 0}


def descartar_carta(card_id: int, player_id: int, juego: Juego):
    validar_carta(card_id, player_id, juego)
    juego.mazo_descarte.append(card_id)
    jugador = get_jugador(player_id, juego)
    jugador.descartar_carta(card_id)


def validar_carta(card_id: int, player_id: int, juego: Juego):
    jugador = get_jugador(player_id, juego)
    if not (card_id in jugador.cartas):
        raise HTTPException(
            status_code=400, detail="El jugador no posee esta carta")


def check_turno(jugador: JugadorPartida):
    if not jugador.get_turno():
        raise HTTPException(
            status_code=400, detail="No es el turno del jugador.")

def check_la_cosa(jugador: JugadorPartida):
    if not jugador.get_la_cosa():
        raise HTTPException(
            status_code=400, detail="El jugador no es la cosa.")

def check_cantidad_cartas(jugador: JugadorPartida):
    if len(jugador.cartas) == 5:
        raise HTTPException(
            status_code=400, detail="No puedes tener mas de 5 cartas en la mano.")

        
def check_objetive_is_next(proximo_jugador: JugadorPartida, juego: Juego):
    if juego.sentido == 1:
        turnoaux = (juego.turno + 2) % len(juego.posiciones)
    elif juego.sentido == -1:
        turnoaux = (juego.turno - 2) % len(juego.posiciones)
    if proximo_jugador.id!= juego.posiciones[turnoaux]:
        raise HTTPException(
            status_code=400, detail="El jugador objetivo no es el proximo en jugar.")
    
def check_obstaculo(atacante_id,objetivo_id, juego: Juego):
    len_posiciones = len(juego.posiciones)
    indice_objetivo = juego.posiciones.index(objetivo_id)
    indice_atacante = juego.posiciones.index(atacante_id)
    indice_posicion_intermedia = get_posicion_intermedia(
        len_posiciones, indice_objetivo, indice_atacante)
    
    validar_obstaculo(indice_posicion_intermedia, juego)

def check_carta_habilitada(card_id: int, jugador_orig: JugadorPartida, jugador_objetivo: JugadorPartida):
    if card_id == 1 :
        raise HTTPException(
            status_code=400, detail="No puedes descartar la carta la cosa.")
    mano = jugador_orig.get_cartas()
    for c in mano:
        if c["id"] in [2, 3, 4, 5, 6, 7, 8, 9, 10,11,12,13,14,15,16,17,18,19,20,21] :
            cantidad_cartas_infectados =+1
    if jugador_orig.get_infectado() and cantidad_cartas_infectados<2 and card_id in [2, 3, 4, 5, 6, 7, 8, 9, 10,11,12,13,14,15,16,17,18,19,20,21]:
        raise HTTPException(
            status_code=400, detail="No puedes descartar la unica carta de infectado que tienes.")
        
    if not jugador_orig.get_la_cosa() and card_id in [2, 3, 4, 5, 6, 7, 8, 9, 10,11,12,13,14,15,16,17,18,19,20,21]:
        raise HTTPException(
            status_code=400, detail="No puedes intercambiar una carta de infectado si no eres la cosa ni infectado.")
    
    if jugador_orig.get_infectado() and not jugador_objetivo.get_la_cosa() and card_id in [2, 3, 4, 5, 6, 7, 8, 9, 10,11,12,13,14,15,16,17,18,19,20,21]:
        raise HTTPException(
            status_code=400, detail="No puedes intercambiar una carta de infectado si no eres la cosa.")