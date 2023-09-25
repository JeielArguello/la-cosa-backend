from models.database import*
from typing import Dict


def get_db() -> Database:
    return db

@db_session
def db_create_user(db: Database, nombre: str) -> Dict[str, int]:
    user_in_db = db.Jugador(nombre = nombre)
    user_in_db.flush()
    result = {"user_name": user_in_db.nombre, "id": user_in_db.id}
    return result
