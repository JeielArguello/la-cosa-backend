from pony.orm import *


db = Database()


class Jugador(db.Entity):
    id = PrimaryKey(int, auto=True)
    # _table_ = 'Partida'
    nombre = Required(str)
    id_avatar = Required(int)
    partida = Optional('Partida')
    


class Partida(db.Entity):
    id = PrimaryKey(int, auto=True)
    nombre = Required(str)
    iniciado = Required(bool)
    id_jugador_creador = Required(int)
    minimo_jugadores = Required(int)
    maximo_jugadores = Required(int)
    contrasena = Optional(str, nullable=True, default=None)
    jugadores = Set(Jugador)


class Carta(db.Entity):
    id = PrimaryKey(int, auto=True)
    nombre = Required(str)
    numero_jugadores = Required(int)
    tipo_dorso = Required(int)
    tipo_de_accion = Required(str)
    descripcion = Optional(str)


def create_db():
    # Conecta a la base de datos SQLite en el archivo 'database.sqlite'
    db.bind(provider='sqlite', filename='database.sqlite', create_db=True)
    # Genera las tablas en la base de datos
    db.generate_mapping(create_tables=True)
