from pony.orm import db_session
from .database import * 

"""
MATCH
"""

@db_session
def init_match(match : Partida):
    match_db = Partida