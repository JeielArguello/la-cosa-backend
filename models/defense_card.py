

from fastapi import HTTPException
from models.player import JugadorPartida
# from models.game import Juego
# from utils.game_utils import jugar_la_carta, get_name_carta


class Defensa:
    def __init__(self, player_orig: JugadorPartida, card_id: int,
                 player_objetive: JugadorPartida) -> None:
        self.atacante = player_orig
        self.defensor = player_objetive
        self.carta_atacante = card_id
        self.carta_defensor = None

    def check_defensor(self, player_id: int):
        if self.defensor.id != player_id:
            raise HTTPException(
                status_code=400,
                detail="No eres el receptor del ataque")

    def completar_ataque(self, card_id: int):
        self.carta_defensor = card_id
        self.atacante.descartar_carta(self.carta_atacante)
