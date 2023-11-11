# from fastapi import HTTPException
from sys import call_tracing
from models.game import Juego
from models.player import JugadorPartida
from utils.action_utils import *
from models.crud import get_name


def play_cuerdas_podridas(player_orig: int, juego: Juego):
    for jugador in juego.jugadores_en_partida:
        if jugador.get_cuartena():
            jugador.remove_cuartena()
    jugador = get_jugador(player_orig, juego)
    msg = {
        "mensaje": jugador.name +
        " jugó la carta Cuerdas Podridas."}
    juego.agregar_log(msg["mensaje"])
    juego.agregar_log(
        jugador.name + " eliminó todas las cuarentenas del juego.")
    return msg


def play_es_aqui_la_fiesta(player_orig: int, juego: Juego):
    # drop cuarentenas
    for jugador in juego.jugadores_en_partida:
        if jugador.get_cuartena():
            jugador.remove_cuartena()
    # drop puertas
    for index in range(0, len(juego.posiciones)):
        if juego.posiciones[index] == "p":
            juego.posiciones[index] = 0
    # cambios de lugar hacia la izquierda (-2)
    index_inicio = juego.posiciones.index(player_orig)
    cantidad_jugadores = (len(juego.posiciones)/2)
    if cantidad_jugadores % 2 == 0:
        cantidad_intercambios = int(cantidad_jugadores/2)
    else:
        cantidad_intercambios = int((cantidad_jugadores-1)/2)
    index = index_inicio
    for i in range(0, cantidad_intercambios):
        aux = juego.posiciones[index]
        juego.posiciones[index] = juego.posiciones[index-2]
        juego.posiciones[index-2] = aux
        index = index-4

    jugador = get_jugador(player_orig, juego)
    msg = {
        "mensaje": jugador.name +
        " jugó la carta Es Aqui la Fiesta?."}
    juego.agregar_log(msg["mensaje"])
    juego.agregar_log(
        jugador.name + " eliminó todos los obstaculos del juego e hizo cambios de lugar.")
    return msg


def play_tres_cuatro(player_orig: int, juego: Juego):
    for index in range(0, len(juego.posiciones)):
        if juego.posiciones[index] == "p":
            juego.posiciones[index] = 0
    jugador = get_jugador(player_orig, juego)
    msg = {
        "mensaje": jugador.name +
        " jugó la carta Tres,Cuatro..."}
    juego.agregar_log(msg["mensaje"])
    juego.agregar_log(
        jugador.name + " eliminó todas las puertas atrancadas.")
    return msg


def play_ups(atacante_in: int, juego: Juego):
    jugador = get_jugador(atacante_in, juego)
    if jugador:
        cartas = jugador.get_cartas()
        msg = {
            "mensaje": jugador.name + " jugó la carta ¡Ups!",
            "cartaMostrar": cartas
        }
        juego.agregar_log(msg["mensaje"])
        juego.agregar_log(
            jugador.name + " mostró su mano de cartas.")
        return (msg)
    else:
        return {"error": "no se pudieron mostrar cartas."}


def play_que_quede_entre_nosotros(player_at: int, player_obj: int, juego: Juego):
    jugador_atacante = get_jugador(player_at, juego)
    jugador_objetivo = get_jugador(player_obj, juego)
    if jugador_atacante and jugador_objetivo:
        cartas = jugador_atacante.get_cartas()
        msg = {
            "mensaje": jugador_atacante.name + " jugó la carta Que quede entre nosotros...",
            "cartaMostrar": cartas
        }
        juego.agregar_log(msg["mensaje"])
        juego.agregar_log(
            jugador_atacante.name + " mostró su mano de cartas a "+jugador_objetivo.name+".")
        return (msg)
    else:
        return {"error": "no se pudieron mostrar cartas"}


def play_cita_a_ciegas(jugador:JugadorPartida, card_id:int, juego:Juego):
    jugador.descartar_carta(card_id)
    juego.mazo_descarte.append(card_id)
    juego.robar_carta_no_panico(jugador)
    msg = { "mensaje": jugador.name + " robo carta, cita a ciegas;por ser de pánico, sé jugo inmediatamente. ",}
    return msg

def play_vuelta_y_vuelta(player_orig : int , juego : Juego):
    jugador = juego.get_jugador(player_orig)

    juego.finalizar_vuelta_y_vuelta(jugador)
    
    jugador_turno = juego.get_jugador_en_turno()
    msg = {
        "mensaje": jugador_turno.name + " jugó la carta Vuelta y Vuelta",
    }
    if juego.sentido == -1:
        sentido_juego = "izquierda"
    else:
        sentido_juego = "derecha"

    juego.agregar_log(msg["mensaje"])
    juego.agregar_log("Todos los jugadores le dieron una carta al jugaador de su " + sentido_juego)
    return (msg)
    

def play_olvidadizo(juego: Juego, player_orig: int, card_id: int):
    jugador = get_jugador(player_orig, juego)
    cartas = jugador.get_cartas()
    if jugador and {"id":card_id} in cartas:        
        cartas_copia = cartas.copy()
        c1 = cartas_copia.pop()
        c2 = cartas_copia.pop()
        c3 = cartas_copia.pop()
        c4 = cartas_copia.pop()
        del cartas_copia

        if c1["id"] != card_id:
            jugador.descartar_carta(c1["id"])
            juego.mazo_descarte.append(c1["id"])
        if c2["id"] != card_id:
            jugador.descartar_carta(c2["id"])
            juego.mazo_descarte.append(c2["id"])
        if c3["id"] != card_id:
            jugador.descartar_carta(c3["id"])
            juego.mazo_descarte.append(c3["id"])    
        if c4["id"] != card_id:
            jugador.descartar_carta(c4["id"])
            juego.mazo_descarte.append(c4["id"])
        for i in range(3):
            juego.robar_carta_no_panico(jugador)
        msg = {"mensaje": jugador.name + " jugó carta Olvidadizo"}
        juego.agregar_log(msg["mensaje"])
        juego.agregar_log(jugador.name + " elimino tres cartas de su mano y robó tres cartas Aléjate.")        
        return(msg)
    else:
        return {"error": "no se pudo descartar o robar cartas."}

