from pony.orm import *
from .database import *
from .database_utils import *
from typing import Dict
from pony.orm import *


# # CARTA
# Create
# Read
@db_session
def read_carta(id: int) -> Carta:
    carta = get(c for c in Carta if c.id == id)
    return carta
# Update
# Delete


# # PARTIDA
# Create
@db_session
def crear_partida(id_usuario_creador, id_name, contraseña,
                  num_max_jugadores, num_min_jugadores):
    user = Jugador.get(id=id_usuario_creador)
    partida = Partida(id_jugador_creador=id_usuario_creador, nombre=id_name,
                      iniciado=False, contrasena=contraseña,
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
def get_estado_partida(match_id: int) -> Dict[bool, int]:
    # Dict[bool, str, int, int, int]
    partida = Partida.get(id=match_id)
    if(partida is None):
        raise HTTPException(detail="La partida no existe")
    cantidad_jugadores = partida.jugadores.count()
    estado = {'iniciada': partida.iniciado,
              'cantidad_jugadores': cantidad_jugadores}
    # estado = {
    #     'iniciada': partida.iniciado,
    #     'nombre_partida': partida.nombre,
    #     'minimo': partida.minimo_jugadores,
    #     'maximo': partida.maximo_jugadores,
    #     'cantidad_jugadores': cantidad_jugadores}
    return estado
# Update


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

# # USUARIO
# Create


@db_session
def db_create_user(nombre: str) -> Dict[str, int]:
    jugador = Jugador(nombre=nombre)
    jugador.flush()
    result = {"user_name": jugador.nombre, "id": jugador.id}
    return result
# Read
# Update
# Delete
