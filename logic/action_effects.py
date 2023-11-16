import random
from fastapi import HTTPException
from models.crud import get_name_carta
from models.game import Juego
from utils.action_utils import *
from models.game import Juego


def play_lanzallamas(atacante_in: int, objetivo_in: int, juego: Juego):
    # get indices
    len_posiciones = len(juego.posiciones)
    indice_objetivo = juego.posiciones.index(objetivo_in)
    indice_atacante = juego.posiciones.index(atacante_in)
    jugador_objetivo = juego.get_jugador(objetivo_in)
    jugador_atacante = juego.get_jugador(atacante_in)

    indice_posicion_intermedia = juego.get_posicion_intermedia(
        objetivo_in, atacante_in)
    # check vecinos
    juego.validar_posiciones_vecinas(
        atacante_in,
        objetivo_in)
    # check obstaculos
    validar_cuarentena(atacante_in,juego)
    validar_obstaculo(indice_posicion_intermedia, juego)
    for jugador in juego.jugadores_en_partida:
        if jugador.id == objetivo_in:
            jugador.set_muerto()
    del juego.posiciones[indice_objetivo]
    if juego.posiciones[indice_objetivo] == "p":
        indiceaux = (indice_objetivo - 1) % len(juego.posiciones)
        juego.posiciones[indiceaux] = "p"
        del juego.posiciones[indice_objetivo]
    else: 
        del juego.posiciones[indice_objetivo]
    if indice_atacante == max(indice_atacante, indice_objetivo):
        juego.turno = (juego.turno - 2) % len(juego.posiciones)
    msg = {
        "mensaje": jugador_atacante.name +
        " jugó carta lanzallamas contra " +
        jugador_objetivo.name}
    juego.agregar_log(msg["mensaje"])
    juego.agregar_log(jugador_objetivo.name + " murió calcinado por " + jugador_atacante.name)
    return msg


def play_hacha(atacante_in: int, objetivo_in: int, juego: Juego):
    
    indice_posicion_intermedia = juego.get_posicion_intermedia(atacante_in, objetivo_in)
    iguales = atacante_in == objetivo_in
    if not iguales:
        juego.validar_posiciones_vecinas(atacante_in, objetivo_in)
    jugador_orig = get_jugador(atacante_in, juego)
    jugador_objetivo = get_jugador(objetivo_in, juego)
    saco_puerta = False
    saco_cuarentena = False
    if is_puerta(indice_posicion_intermedia, juego):
        juego.posiciones[indice_posicion_intermedia] = 0
        saco_puerta = True
    elif is_cuarentena(objetivo_in, juego):
        jugador_objetivo.remove_cuartena()
        saco_cuarentena = True
    else:
        validar_puerta(indice_posicion_intermedia, juego)
    msg = {
        "mensaje": jugador_orig.name +
        " jugó carta hacha contra " +
        jugador_objetivo.name}
    juego.agregar_log(msg["mensaje"])
    if saco_cuarentena:
        if iguales:
            juego.agregar_log(jugador_orig.name + " rompió su propia cuarentena")
        else:
            juego.agregar_log(jugador_orig.name + " elimino la cuarentena de " + jugador_objetivo.name)
    if saco_puerta:
        juego.agregar_log(jugador_orig.name + " rompió la puerta atrancada con una hacha" )
    return msg


def play_sospecha(atacante_in: int, objetivo_in: int, juego: Juego):
    jugador_objetivo = get_jugador(objetivo_in, juego)
    jugador_atacante = get_jugador(atacante_in, juego)
    carta_id = random.choice(jugador_objetivo.cartas)
    if carta_id not in jugador_objetivo.cartas:
        raise HTTPException(
            status_code=400,
            detail="No se pudo obtener una carta del jugador objetivo")
    msg = {"mensaje": jugador_atacante.name +
           " jugó carta sospecha contra " +
           jugador_objetivo.name, "cartaMostrar": [{"id": carta_id}]}
    juego.agregar_log(msg["mensaje"])
    juego.agregar_log(jugador_atacante.name + " miro una carta de " + jugador_objetivo.name)
    return msg


def play_vigila_tus_espaldas(juego: Juego):
    juego.sentido = juego.sentido * (-1)


def play_mas_vale_que_corras(atacante_in: int, objetivo_in: int, juego: Juego):
    # validar si esta en cuarentena
    validar_cuarentena(objetivo_in, juego)
    validar_cuarentena(atacante_in, juego)
    # obtengo jugadores
    jugador_atacante = get_jugador(atacante_in, juego)
    jugador_objetivo = get_jugador(objetivo_in, juego)
    # obtengo el indice de los jugadores
    indice_objetivo = juego.posiciones.index(objetivo_in)
    indice_atacante = juego.posiciones.index(atacante_in)
    # hago el intercambio de posiciones
    juego.posiciones[indice_objetivo] = atacante_in
    juego.posiciones[indice_atacante] = objetivo_in
    jugador_atacante.posicion = indice_objetivo
    jugador_objetivo.posicion = indice_atacante

    juego.turno = indice_objetivo
    jugador_orig = get_jugador(atacante_in, juego)
    jugador_objetivo = get_jugador(objetivo_in, juego)
    msg = {
        "mensaje": jugador_orig.name +
        " jugó carta ¡Más vale que corras! contra " +
        jugador_objetivo.name}
    juego.agregar_log(msg["mensaje"])
    juego.agregar_log(jugador_objetivo.name + " cambió de lugar con " + jugador_atacante.name)
    return msg


def play_whisky(atacante_in: int, juego: Juego, card_id: int):
    jugador = get_jugador(atacante_in, juego)
    if jugador:
        cartas = jugador.get_cartas()
        cartas.remove({"id": card_id})
        msg = {
            "mensaje": jugador.name + " jugó carta Whisky.",
            "cartaMostrar": cartas
        }
        juego.agregar_log(msg["mensaje"])
        juego.agregar_log(jugador.name + " mostró su mano de cartas")
        return (msg)
    else:
        return {"error": "no se pudieron mostrar cartas."}


def play_cambio_de_lugar(
        juego: Juego,
        player_orig: int,
        player_objective: int):

    posiciones = juego.posiciones
    posPorg = posiciones.index(player_orig)
    posPobj = posiciones.index(player_objective)
    
    validar_cuarentena(player_objective, juego)
    validar_cuarentena(player_orig, juego)

    juego.validar_posiciones_vecinas(player_objective, player_orig)

    posiciones[posPorg] = player_objective
    posiciones[posPobj] = player_orig

    jugadoresEnPartida = juego.jugadores_en_partida
    indexPOrg = next((i for i, jugador in enumerate(
        jugadoresEnPartida) if jugador.id == player_orig), None)
    indexPobj = next((i for i, jugador in enumerate(
        jugadoresEnPartida) if jugador.id == player_objective), None)

    pOrg = jugadoresEnPartida[indexPOrg]
    pObj = jugadoresEnPartida[indexPobj]

    pOrg.posicion = posPobj
    pObj.posicion = posPorg

    juego.turno = posPobj
    jugador_orig = get_jugador(player_orig, juego)
    jugador_objetivo = get_jugador(player_objective, juego)
    msg = {
        "mensaje": jugador_orig.name +
        " jugó carta ¡Cambio de lugar! contra " +
        jugador_objetivo.name}
    juego.agregar_log(msg["mensaje"])
    juego.agregar_log(jugador_objetivo.name + " cambió de lugar con " + jugador_orig.name )
    return msg


def play_analisis(juego: Juego, player_orig: int, player_objective: int):
    
    juego.validar_posiciones_vecinas(player_objective, player_orig)
    playerOrig = get_jugador(player_orig, juego)
    playerObj = get_jugador(player_objective, juego)
    manoPlayerObj = playerObj.get_cartas()
    msg = {
        "mensaje": playerOrig.name +
        " jugó carta Análisis contra " +
        playerObj.name +
        ".",
        "cartaMostrar": manoPlayerObj}
    juego.agregar_log(msg["mensaje"])
    juego.agregar_log(playerOrig.name + " analizo la mano de " + playerObj.name)
    return msg

def play_seduccion(juego: Juego, player_orig : int, player_objective: int):
    jugador_atacante = get_jugador(player_orig, juego)
    jugador_objetivo = get_jugador(player_objective, juego)
    #aqui deberia chequear cuarentena posiblemente.
    validar_cuarentena(player_objective, juego)
    if not is_cuarentena(player_objective, juego):
        jugador_objetivo.set_efecto_seduccion()
        msg = {"mensaje": jugador_atacante.name + " jugó carta Seducción contra "
                + jugador_objetivo.name + "."}
    else:
        msg = {"mensaje": "error "
                + jugador_objetivo.name + " en cuarentena."}
    juego.agregar_log(msg["mensaje"])
    juego.agregar_log(jugador_atacante.name + " sedujo a " + jugador_objetivo.name +" para realizar un intercambio de cartas")
    return msg

def play_determinacion(juego: Juego, player_orig: int):
    playerOrig = get_jugador(player_orig, juego)
    cartas_determinacion = juego.robar_carta_determinacion()
    msg = {"mensaje": playerOrig.name +
           " jugó carta Determinación.", "cartas": cartas_determinacion}
    juego.agregar_log(msg["mensaje"])
    return msg


