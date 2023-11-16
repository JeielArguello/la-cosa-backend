from fastapi import HTTPException, status
from pony.orm import *
from .database import *


def get_db() -> Database:
    return db

# USUARIO


@db_session
def get_exist_user(id_user: int):
    jugador_en_db = Jugador.get(id=id_user)
    return jugador_en_db is not None

# PARTIDA


@db_session
def listar_partidas():
    list_rooms = []

    partidas = get_matches()
    for partida in partidas:
        cant_jugadores = db_cantidad_jugadores(partida.id)
        if cant_jugadores is None:
            raise HTTPException(
                status_code=400,
                detail="No se pudo obtener la partida")

        if not partida.iniciado and cant_jugadores < partida.maximo_jugadores:
            list_rooms.append({'id_partida': partida.id,
                               'name_partida': partida.nombre,
                               'cantidad_jugadores': cant_jugadores,
                               'cantidad_jugadores_maximos': partida.maximo_jugadores,
                               'contrasena': (partida.contrasena is not None),
                               'iniciado': partida.iniciado})
    return list_rooms


@db_session
def validar_entrada_partida(id_player: int, id_match: int, contrasena: str):
    # existe el usuario
    if not get_exist_user(id_player):
        raise ValueError("Usuario no existe")
    # usuario en otra partida
    if get_exist_user_in_game(id_player):
        raise ValueError("Usuario ya ingresado en una partida")
    # existe partida
    if not get_exist_match(id_match):
        raise ValueError("Partida no existe")
    partida = get_match(id_match)
    if partida is None:
        raise HTTPException(
            detail="no se pudo cargar la partida de base de datos")
    if not get_partida_habilitada(partida):
        raise ValueError("Partida llena")
    if partida.iniciado:
        raise ValueError("Partida ya iniciada")
    if partida.contrasena != contrasena:
        raise ValueError("Contraseña incorrecta")


@db_session
def get_partida_habilitada(partida_select: Partida):
    cantidad_jugadores = partida_select.jugadores.count()
    cantidad_max = partida_select.maximo_jugadores
    return cantidad_max > cantidad_jugadores


@db_session
def get_exist_user_in_game(id_user: int):
    jugador = get(p for p in Jugador if p.id == id_user)
    check = jugador.partida is not None
    return check


@db_session
def get_match(match_id: int):
    match = get(p for p in Partida if p.id == match_id)
    return match


@db_session
def get_jugadores_match(posiciones: list):
    jugadores = []
    for j in posiciones:
        if j != 0 and j != "p":
            id = j
            nombre = get_name(id)
            id_avatar = get_id_avatar(id)
            jugador = {'id': id, 'nombre': nombre,'id_avatar':id_avatar}
            jugadores.append(jugador)
    return jugadores

@db_session
def get_id_avatar(user_id: int) -> str:
    user = get(u for u in Jugador if u.id == user_id)
    return user.id_avatar

@db_session
def get_name(user_id: int) -> str:
    user = get(u for u in Jugador if u.id == user_id)
    return user.nombre


@db_session
def get_exist_match(id_match: int):
    match_in_db = Partida.get(id=id_match)
    return match_in_db is not None


@db_session
def database_utils_iniciar_partida(match_id: int, user_id: int):

    partida = Partida.get(id=match_id)

    if partida is None:
        raise HTTPException(status_code=400, detail="El match_id no es válido")

    if partida.id_jugador_creador != user_id:
        raise HTTPException(
            status_code=400,
            detail="El user_id no corresponde al creador de la partida")

    if partida.iniciado:
        raise HTTPException(
            status_code=400, detail="La partida ya esta inicializada.")

    if partida.jugadores.count() < partida.minimo_jugadores:
        raise HTTPException(
            status_code=400,
            detail="No se cumple la cantidad minima de jugadores.")

    partida.iniciado = True

    if not partida.iniciado:
        raise HTTPException(
            status_code=400, detail="No se puede inicializar la partida. ")


@db_session
def construir_mazo(num_jugadores: int):
    if num_jugadores > 3 and num_jugadores < 13:
        try:
            cartas_seleccionadas = select(
                c.id for c in Carta if c.numero_jugadores <= num_jugadores)
            mazo = list(cartas_seleccionadas)
            return mazo
        except Exception as e:
            return {"error al construir el mazo"}
    else:
        return {"error": "numero de jugadores incorrecto"}


@db_session
def get_jugadores_en_juego(partida: Partida):
    try:
        if partida is not None:
            jugadores = partida.jugadores
            return jugadores
    except Exception as e:
        return {"error al obtener jugadores en la partida"}


@db_session
def get_matches():
    matches = select(p for p in Partida)
    return matches


@db_session
def db_cantidad_jugadores(match_id):
    partida = Partida.get(id=match_id)
    cantidad_jugadores = partida.jugadores.count()
    return cantidad_jugadores
