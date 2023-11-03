

from fastapi import HTTPException
from models.player import JugadorPartida


class IntercambiarCarta:
    def __init__(self, player_orig: JugadorPartida, card_id: int,
                 player_objetive: JugadorPartida) -> None:
        self.soliciatante = player_orig
        self.receptor = player_objetive
        self.carta_solicitante = card_id
        self.carta_receptor = None

    def check_receptor(self, player_id: int):
        if self.receptor.id != player_id:
            raise HTTPException(
                status_code=400,
                detail="No eres el receptor del intercambio")

    def completar_intercambio(self, card_id: int):
        self.carta_receptor = card_id
        if self.soliciatante.get_la_cosa() and self.carta_solicitante in [
                2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]:
            self.receptor.set_infectado()
        if self.receptor.get_la_cosa() and self.carta_receptor in [
                2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]:
            self.soliciatante.set_infectado()
        self.soliciatante.descartar_carta(self.carta_solicitante)
        self.receptor.descartar_carta(self.carta_receptor)
        self.soliciatante.agregar_carta(self.carta_receptor)
        self.receptor.agregar_carta(self.carta_solicitante)
