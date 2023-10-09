from models.crud import read_carta
from fastapi import WebSocket
from typing import List
import random
from logic.deck import deck_es_carta_alejate
from logic.player import JugadorPartida
from fastapi import HTTPException


class Juego:
    def __init__(self, partida_id: int, cantidad_jugadores: int, creador: int,
                 jugadores_id: list[int]):
        self.partida_id = partida_id
        self.cantidad_jugadores = cantidad_jugadores
        self.creador = creador
        self.jugadores_id = jugadores_id

        self.jugadores_en_partida: List[JugadorPartida] = []
        self.sentido = 1
        self.turno = -1
        self.mazo: List[int] = []
        self.mazo_descarte = []
        self.posiciones = []
        self.ws_players_game: List[WebSocket] = []

        # spawnear jugadores
        crear_jugadores_partida(self)
        # otorgar posiciones
        otorgar_posiciones(self)
        # # crear mazo
        # construir_mazo(self)
        # # repartir cartas
        # repartir_cartas(self, cantidad_jugadores)

    # def manejar_turnos(juego: Juego):
    #     if juego.sentido == 1:
    #         juego.turno = (juego.turno + 1) % len(juego.jugadores_en_partida)
    #     elif juego.sentido == 0:
    #         juego.turno = (juego.turno - 1) % len(juego.jugadores_en_partida)

        jugador = self.jugadores_en_partida[self.turno]
        jugador.cambiar_turno()
        print("manejador turno")

    def jugar_partida(self):
        while True:
            self.manejar_turnos()
            self.jugar_turno()
            # chequear ganador
            # la cosa muerta?
            # todos infectado?
            #
            # if hay_ganador:
            #     break
        # notificar resultados
        # finalizar partida
        print("partida")
    
    #Funciones para conexion del websocket
    async def connect_game(self, websocket: WebSocket):
        await websocket.accept()
        self.ws_players_game.append(websocket)
        await self.broadcast_global({"message": "se agrego un usuario al game"})
        
    async def disconnect_game(self, websocket: WebSocket):
        self.ws_players_game.remove(websocket)
        await websocket.send_text("cerrando conexion")
        await websocket.close(reason="cliente pide desconexion")
        await self.broadcast_global("se desconecto un usuario")
    
    async def broadcast_global(self, message: dict):
        for p in self.ws_players_game:
            await p.send_json(message)

    def repartir_cartas(self, players_num: int):
        # Convierte el conjunto a una lista para poder acceder por índice
        mazo = list(self.mazo)
        indice_la_cosa = random.randint(0, players_num - 1)
        # range(0, 5) generará los números del 0 al
        for iteration in range(0, 4):  # se deben repartir cuatro cartas a cada jugador
            # por cada jugador en la partida
            for indexJugador in range(0, len(self.jugadores_en_partida)):
                jugador = self.jugadores_en_partida[indexJugador]
                if iteration == 0 and indexJugador == indice_la_cosa:  # Corregir esta línea
                    # el id 1 corresponde a la carta la cos
                    jugador.agregar_carta(1)
                    jugador.la_cosa = True
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


def robar_carta(juego: Juego, jugador: JugadorPartida):
    if len(juego.mazo) == 0:
        raise HTTPException(
            status_code=400,
            detail="El mazo esta vacio")
    carta_id = juego.mazo.pop()
    jugador.agregar_carta(carta_id)


def crear_jugadores_partida(juego: Juego):
    jugadores_id = juego.jugadores_id
    for id in jugadores_id:
        jugador = JugadorPartida(id)
        juego.jugadores_en_partida.append(jugador)


def otorgar_posiciones(juego: Juego):
    for jugador_id in juego.jugadores_id:
        juego.posiciones.append(jugador_id)
        juego.posiciones.append(0)
