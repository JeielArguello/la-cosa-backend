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

def play_cita_a_siegas(jugador:JugadorPartida, card_id:int, juego:Juego):
    jugador.descartar_carta(card_id)
    juego.mazo_descarte.append(card_id)
    juego.robar_carta_no_panico(jugador)
    msg = { "mensaje": jugador.name + " robo carta, cita a ciegas;por ser de pánico, sé jugo inmediatamente. ",}
    return msg