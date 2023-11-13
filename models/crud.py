from pony.orm import *
from .database import Carta, Partida, Jugador
from .database_utils import get_exist_user, get_match
from typing import Dict
from fastapi import HTTPException


# # CARTA
# Create
# Read
@db_session
def read_carta(id: int) -> Carta:
    carta = get(c for c in Carta if c.id == id)
    return carta


@db_session
def get_name_carta(card_id: int) -> str:
    card = get(u for u in Carta if u.id == card_id)
    return card.nombre


@db_session
def get_dorso_carta(card_id: int) -> str:
    card = get(u for u in Carta if u.id == card_id)
    return card.tipo_dorso
# Update
# Delete


# # PARTIDA
# Create
@db_session
def crear_partida(id_usuario_creador, id_name, contraseña,
                  num_max_jugadores, num_min_jugadores):
    user = Jugador.get(id=id_usuario_creador)

    if contraseña != "" or contraseña != " ":
        partida = Partida(
            id_jugador_creador=id_usuario_creador,
            nombre=id_name,
            iniciado=False,
            contrasena=contraseña,
            maximo_jugadores=num_max_jugadores,
            minimo_jugadores=num_min_jugadores,
            jugadores=[])
    else:
        partida = Partida(
            id_jugador_creador=id_usuario_creador,
            nombre=id_name,
            iniciado=False,
            maximo_jugadores=num_max_jugadores,
            minimo_jugadores=num_min_jugadores,
            jugadores=[])

    if(user is None):
        raise HTTPException(
            detail="No se pudo obtener el usuario de la base de datos.")
    if(partida is None):
        raise HTTPException(
            detail="No se pudo inicializar la partida en base de datos.")

    partida.jugadores.add(user)
    partida.flush()
    result = {"id_partida": partida.id}
    return result


# Read


@db_session
def get_estado_partida(match_id: int) -> Dict:
    # Dict[bool, str, int, int, int]
    partida = Partida.get(id=match_id)
    if(partida is None):
        raise HTTPException(status_code=400, detail="La partida no existe")
    cantidad_jugadores = partida.jugadores.count()
    estado = {
        'iniciada': partida.iniciado,
        'nombre_partida': partida.nombre,
        'minimo': partida.minimo_jugadores,
        'maximo': partida.maximo_jugadores,
        'cantidad_jugadores': cantidad_jugadores}
    return estado

# Update


@db_session
def models_crud_eliminar_jugador_no_creador_de_pratida_sin_inicializar(
        id_jugador: int, match_id: int):
    partida: Partida = Partida.get(id=match_id)
    if(partida is None):
        raise HTTPException(status_code=400, detail="No se obtuvo la pertida.")
    if(id_jugador != partida.id_jugador_creador):
        jugador = Jugador.get(id=id_jugador)
        if(jugador is None):
            raise HTTPException(
                status_code=400,
                detail="No se obtuvo el jugador.")

        partida.jugadores -= Jugador[id_jugador]
        jugador.partida = None


@db_session
def update_add_player(user_id: int, match_id: int):
    if get_exist_user(user_id):
        user_creator = Jugador.get(id=user_id)
        if(user_creator is None):
            raise HTTPException(detail="No se pudo obtener el usuario")
        match_update = get_match(match_id)
        if(match_update is None):
            raise HTTPException(detail="No se pudo obtener la partida")
        if user_creator is not None and match_update is not None:
            match_update.jugadores.add(user_creator)


# Delete
@db_session
def delete_match(match_id: int):
    match = Partida.get(id=match_id)
    if match:
        match.delete()


@db_session
def delete_match(match_id: int):
    match = Partida.get(id=match_id)
    if match:
        for jugador in match.jugadores:
            jugador.partida = None
        match.delete()


# # USUARIO
# Create


@db_session
def db_create_user(nombre: str,id_avatar:int) -> Dict[str, int]:
    jugador = Jugador(
                    nombre=nombre,
                    id_avatar = id_avatar)
    jugador.flush()
    
    result = {"user_name": jugador.nombre, "id": jugador.id}
    return result

# Read


@db_session
def get_name(user_id: int) -> str:
    user = get(u for u in Jugador if u.id == user_id)
    return user.nombre

@db_session
def get_id_avatar(user_id: int) -> str:
    user = get(u for u in Jugador if u.id == user_id)
    return user.id_avatar


# Update
# Delete
