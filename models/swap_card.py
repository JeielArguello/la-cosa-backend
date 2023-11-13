

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

    # Esta funcion deberia cambiar el receptor del intercambio al jugador pasado por parametro
    def cambiar_receptor(self, nuevo_receptor: JugadorPartida):
        self.receptor = nuevo_receptor



class IntercambiarCartaVyv:
    def __init__(self, player_orig: JugadorPartida, cant_jugadores : int) -> None:
        self.primer_jugador = player_orig
        self.cartas_intercambio = [] 
        self.list_jugadores = []
        self.is_complete = False
        self.total_jugadores = cant_jugadores
        self.ultimo_jugador: JugadorPartida = None
        self.lacosa_indice = None

    def is_complete_vuelta_y_vuelta(self):
        return self.is_complete
    
    def completar_vuelta_y_vuelta(self,jugador: JugadorPartida, card_id: int):
        if card_id not in jugador.cartas:
            raise HTTPException(
                status_code=400,
                detail="No tienes la carta que quieres intercambiar")
        self.list_jugadores.append(jugador)
        self.cartas_intercambio.append(card_id)
        if jugador.get_la_cosa():
            print("La cosa", jugador.name)
            self.lacosa_indice = len(self.list_jugadores) - 1
        if len(self.cartas_intercambio) == self.total_jugadores:
            self.is_complete = True
            self.ultimo_jugador = jugador


    def realizar_intercambios(self):

        for i in range(0, len(self.list_jugadores)):
            self.list_jugadores[i].descartar_carta(self.cartas_intercambio[i])
            self.list_jugadores[i].agregar_carta(self.cartas_intercambio[(i-1)%len(self.list_jugadores)])
            if self.lacosa_indice is not None and (i-1)%len(self.list_jugadores) == self.lacosa_indice and self.cartas_intercambio[(i-1)%len(self.list_jugadores)] in [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]:
                self.list_jugadores[i].set_infectado()
        
