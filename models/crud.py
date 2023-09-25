from models.database import *
from pony.orm import *


# Carta
# READ
@db_session
def read_carta(id: int) -> Carta:
    carta = get(c for c in Carta if c.id == id)
    return carta
