import random
from logic.deck import deck_es_carta_alejate
from models.database_utils import construir_mazo
from models.player import JugadorPartida
from fastapi import HTTPException, WebSocket
# from logic.deck import robar_carta
from typing import List
from pony.orm import *
from models.database import *


class Juego:
    def __init__(self, partida_id: int, cantidad_jugadores: int, creador: int,
                 jugadores_id: list[int]):
        self.partida_id = partida_id
        self.cantidad_jugadores = cantidad_jugadores
        self.creador = creador
        self.jugadores_id = jugadores_id

        self.jugadores_en_partida: List[JugadorPartida] = []
        self.sentido = 1
        self.turno = 0
        self.mazo: List[int] = []
        self.mazo_descarte = []
        self.posiciones = []

        self.ws_players_game: List[WebSocket] = []

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
        for p in self.jugadores_en_partida:
                if p.id == player_id:
                    jugador = p 
        await jugador.ws_player.send_json(message)



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
        juego.posiciones.append(0)
