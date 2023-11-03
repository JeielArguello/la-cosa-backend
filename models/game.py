import random
from logic.deck import deck_es_carta_alejate
from models.database_utils import construir_mazo
from models.player import JugadorPartida
from fastapi import HTTPException, WebSocket
# from logic.deck import robar_carta
from typing import List
from pony.orm import *
from models.database import *
from models.swap_card import IntercambiarCarta


class Juego:
    def __init__(self, partida_id: int, cantidad_jugadores: int, creador: int,
                 jugadores_id: list[int]):
        self.partida_id = partida_id
        self.cantidad_jugadores = cantidad_jugadores
        self.creador = creador
        self.jugadores_id = jugadores_id

        self.jugadores_en_partida: List[JugadorPartida] = []
        self.sentido = -1
        self.turno = 0
        self.mazo: List[int] = []
        self.mazo_descarte = []
        self.posiciones = []

        self.cartas_determinacion = []

        self.ws_players_game: List[WebSocket] = []
        self.solicitud_intercambio: IntercambiarCarta = None 
        
        # spawnear jugadores
        crear_jugadores_partida(self)
        # otorgar posiciones
        otorgar_posiciones(self)
        # # crear mazo
        self.mazo = construir_mazo(self.cantidad_jugadores)
        # iniciar turnos
        self.jugadores_en_partida[0].cambiar_turno()

    def avanzar_turno(self):
        if self.sentido == 1:
            self.turno = (self.turno + 2) % len(self.posiciones)
        elif self.sentido == -1:
            self.turno = (self.turno - 2) % len(self.posiciones)
        for j in self.jugadores_en_partida:
            if j.id == self.posiciones[self.turno]:
                j.cambiar_turno()

    def terminar_turno(self):
        for j in self.jugadores_en_partida:
            if j.id == self.posiciones[self.turno]:
                j.cambiar_turno()

    def repartir_cartas(self, players_num: int):
        # Convierte el conjunto a una lista para poder acceder por índice
        mazo = list(self.mazo)
        indice_la_cosa = random.randint(0, players_num - 1)
        # range(0, 5) generará los números del 0 al
        for iteration in range(
                0, 4):  # se deben repartir cuatro cartas a cada jugador
            # por cada jugador en la partida
            for indexJugador in range(0, len(self.jugadores_en_partida)):
                jugador = self.jugadores_en_partida[indexJugador]
                if iteration == 0 and indexJugador == indice_la_cosa:  # Corregir esta línea
                    # el id 1 corresponde a la carta la cos
                    jugador.agregar_carta(1)
                    jugador.la_cosa = True
                    jugador.humano = False
                    mazo.remove(1)  # elimina el primer elemento con valor 1
                else:
                    while len(mazo) > 0:
                        indice_random = random.randint(0, len(mazo) - 1)
                        id_carta_seleccionada = mazo[indice_random]
                        if deck_es_carta_alejate(id_carta_seleccionada):
                            jugador.agregar_carta(id_carta_seleccionada)
                            del mazo[indice_random]
                            break

            if iteration == 3:
                self.mazo = mazo
        random.shuffle(self.mazo)
    
    def get_jugador(self, player_id: int):
        for j in self.jugadores_en_partida:
            if j.id == player_id:
                return j

    def get_jugador_en_turno(self):
        for j in self.jugadores_en_partida:
            if j.get_turno():
                return j
    
    def get_jugador_siguiente_turno(self):
        if self.sentido == 1:
            turnoaux = (self.turno + 2) % len(self.posiciones)
        elif self.sentido == -1:
            turnoaux = (self.turno - 2) % len(self.posiciones)
        for j in self.jugadores_en_partida:
            if j.id == self.posiciones[turnoaux]:
                return j
            
    def crear_intercambio(self, player_orig: int, card_id: int, player_objective: int):
        if self.solicitud_intercambio is not None:
            raise HTTPException(
                status_code=400,
                detail="Ya hay una solicitud de intercambio")
        jugador_orig = self.get_jugador(player_orig)
        jugador_objetivo = self.get_jugador(player_objective)
        self.solicitud_intercambio = IntercambiarCarta(jugador_orig, card_id, jugador_objetivo)

    def responder_intercambio(self, player_id: int, card_id: int):
        intercambio = self.solicitud_intercambio
        if intercambio is None:
            raise HTTPException(
                status_code=400,
                detail="No hay solicitud de intercambio")
        intercambio.check_receptor(player_id)
        intercambio.completar_intercambio(card_id)
        self.solicitud_intercambio = None
        del intercambio

    # Funciones para conexion del websocket
    async def connect_game(self, websocket: WebSocket):
        await websocket.accept()
        msg = await websocket.receive_json()
        if  "player_id" in msg:
            for p in self.jugadores_en_partida:
                if p.id == msg["player_id"]:
                    jugador = p  
            jugador.ws_player = websocket
            if jugador.get_turno():
                await self.mensaje_personal(jugador.id,"E")
        else: 
            print("error al conectar jugador")
        self.ws_players_game.append(websocket)
        await self.broadcast_global("C")
        await self.broadcast_global("D")

    async def disconnect_game(self, websocket: WebSocket):
        self.ws_players_game.remove(websocket)
        await websocket.send_text("cerrando conexion")
        await websocket.close(reason="cliente pide desconexion")

    async def broadcast_global(self, message: dict):
        for p in self.ws_players_game:
            await p.send_json(message)
            await p.send_json("reset")

    async def mensaje_personal(self, player_id: int, message: str):
        jugador = self.get_jugador(player_id)
        await jugador.ws_player.send_json(message)
        await jugador.ws_player.send_json("reset")

    def robar_carta_determinacion(self):
        cartas = []
        while len(cartas)<3:
            if len(self.mazo) == 0:
                random.shuffle(self.mazo_descarte)
                self.mazo = self.mazo_descarte
                self.mazo_descarte = []
            carta_id = self.mazo.pop()
            if carta_id in list(range(89, 109)):
                self.mazo_descarte.append(carta_id)
            else:
                cartas.append({"id":carta_id})
                self.cartas_determinacion.append(carta_id)
        return cartas



def robar_carta(juego: Juego, jugador: JugadorPartida):
    if len(juego.mazo) == 0:
        raise HTTPException(
            status_code=400,
            detail="El mazo esta vacio")
    carta_id = juego.mazo.pop()
    jugador.agregar_carta(carta_id)
    if len(juego.mazo) == 0:
        random.shuffle(juego.mazo_descarte)
        juego.mazo = juego.mazo_descarte
        juego.mazo_descarte = []
    return carta_id


def crear_jugadores_partida(juego: Juego):
    jugadores_id = juego.jugadores_id
    for id in jugadores_id:
        jugador = JugadorPartida(id)
        juego.jugadores_en_partida.append(jugador)


def otorgar_posiciones(juego: Juego):
    for jugador_id in juego.jugadores_id:
        juego.posiciones.append(jugador_id)
        jugador = juego.get_jugador(jugador_id)
        jugador.posicion = juego.posiciones.index(jugador_id)
        print(jugador.name + " tiene posicion " + str(jugador.posicion))
        juego.posiciones.append(0)
