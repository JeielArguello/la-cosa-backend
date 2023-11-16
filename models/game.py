import random
from logic.deck import deck_es_carta_alejate
from models.constants import *
from models.database_utils import construir_mazo
from models.player import JugadorPartida
from fastapi import HTTPException, WebSocket
# from logic.deck import robar_carta
from typing import List
from pony.orm import *
from models.database import *
from models.swap_card import IntercambiarCarta, IntercambiarCartaVyv
from models.defense_card import Defensa


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
        self.logs = []

        self.cartas_determinacion = []


        self.ws_players_game: List[WebSocket] = []
        self.solicitud_intercambio: IntercambiarCarta = None
        self.solicitud_ataque: Defensa = None
        self.solicitud_intercambio_vyv: IntercambiarCartaVyv = None

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
        print("terminando turno",self.turno)
        for j in self.jugadores_en_partida:
            if j.id == self.posiciones[self.turno]:
                if j.get_cuartena():
                    j.pop_cuarentena()
                    if not j.get_cuartena():
                        self.agregar_log(j.name + " termino su cuarentena")
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

    # Funciones para turno
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
    
    def get_jugador_anterior_turno(self):
        if self.sentido == 1:
            turnoaux = (self.turno - 2) % len(self.posiciones)
        elif self.sentido == -1:
            turnoaux = (self.turno + 2) % len(self.posiciones)
        for j in self.jugadores_en_partida:
            if j.id == self.posiciones[turnoaux]:
                return j
    
    def get_posicion_de_jugador(self, jugador_id: int):
        indice_jugador = self.posiciones.index(jugador_id)
        return indice_jugador
    
    def is_obstaculo(self, atacante_id:int, objetivo_id: int):
        indice_posicion_intermedia = self.get_posicion_intermedia( objetivo_id, atacante_id)
        hay_obstaculo = False
        if len(self.posiciones) > 4:
            if self.posiciones[indice_posicion_intermedia] != 0 :
                hay_obstaculo = True
        else:
            if self.posiciones[indice_posicion_intermedia] != 0 or self.posiciones[indice_posicion_intermedia+2] != 0:
                hay_obstaculo = True
        return hay_obstaculo
    
    def get_posicion_intermedia(self, jugador1: int, jugador2: int):
        len_posiciones = len(self.posiciones)
        indice_jugador1 = self.get_posicion_de_jugador(jugador1)
        indice_jugador2 = self.get_posicion_de_jugador(jugador2)
        border_one = (indice_jugador1 == 0 and indice_jugador2 ==
                    len_posiciones - 2) and len_posiciones > 4
        border_two = (indice_jugador2 == 0 and indice_jugador1 ==
                    len_posiciones - 2) and len_posiciones > 4
        if (border_one or border_two):
            posicion = len_posiciones - 1
        else:
            posicion = min(indice_jugador1, indice_jugador2) + 1
        return posicion
    
    def validar_posiciones_vecinas(
            self, objetivo_id: int, atacante_id: int):
        len_posiciones = len(self.posiciones)
        indice_objetivo = self.posiciones.index(objetivo_id)
        indice_atacante = self.posiciones.index(atacante_id)
        primero = min(indice_objetivo, indice_atacante)
        segundo = max(indice_objetivo, indice_atacante)
        if (primero + 2 != segundo) and (primero !=
                                        0 or segundo != len_posiciones - 2):
            raise HTTPException(
                status_code=400,
                detail="Los jugadores no son vecinos")

    # Funciones para encontrar proximo jugador
    def get_jugador_siguiente(self, jugador: JugadorPartida):
        indice_jugador = self.get_posicion_de_jugador(jugador.id)
        if self.sentido == 1:
            indice_siguiente = (indice_jugador + 2) % len(self.posiciones)
        elif self.sentido == -1:
            indice_siguiente = (indice_jugador - 2) % len(self.posiciones)
        for j in self.jugadores_en_partida:
            if j.id == self.posiciones[indice_siguiente]:
                return j
            
    
    # Funciones para log
    def get_logs(self):
        return self.logs
    
    def agregar_log(self,log:str):
        self.logs.append(log)

    # Funciones para intercambio
    def crear_intercambio(
            self,
            player_orig: int,
            card_id: int,
            player_objective: int):
        if self.solicitud_intercambio is not None:
            raise HTTPException(
                status_code=400,
                detail="Ya hay una solicitud de intercambio")
        jugador_orig = self.get_jugador(player_orig)
        jugador_objetivo = self.get_jugador(player_objective)
        self.solicitud_intercambio = IntercambiarCarta(
            jugador_orig, card_id, jugador_objetivo)

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

    def iniciar_vuelta_y_vuelta(self, player_orig: JugadorPartida):
        if self.solicitud_intercambio_vyv is not None:
            raise HTTPException(
                status_code=400,
                detail="Ya hay una solicitud de intercambio")
        self.solicitud_intercambio_vyv = IntercambiarCartaVyv(
            player_orig, len(self.posiciones)/2)
    
    def finalizar_vuelta_y_vuelta(self,jugador : JugadorPartida):
        intercambio = self.solicitud_intercambio_vyv
        if intercambio is  None:
            raise HTTPException(
                status_code=400,
                detail="No hay una solicitud de intercambio")
        if intercambio.ultimo_jugador != jugador:
            raise HTTPException(
                status_code=400,
                detail="No eres el jugador que termina el intercambio")
        intercambio.realizar_intercambios()
        self.solicitud_intercambio_vyv = None
        del intercambio

    # Funciones para defensa
    def crear_ataque(
            self,
            player_orig: int,
            card_id: int,
            player_objective: int):
        if self.solicitud_ataque is not None:
            raise HTTPException(
                status_code=400,
                detail="Ya hay una solicitud de ataque")
        jugador_orig = self.get_jugador(player_orig)
        jugador_objetivo = self.get_jugador(player_objective)
        self.solicitud_ataque = Defensa(
            jugador_orig, card_id, jugador_objetivo)

    def responder_ataque(self, player_id: int, card_id: int):
        ataque = self.solicitud_ataque
        if ataque is None:
            raise HTTPException(
                status_code=400,
                detail="No hay solicitud de ataque")
        ataque.check_defensor(player_id)
        ataque.completar_ataque(card_id)
        self.solicitud_ataque = None
        del ataque

    def robar_carta_no_panico(self, jugador: JugadorPartida):
        panico = True
        while panico:
            carta = robar_carta(self, jugador)
            if carta in list(range(89, 109)):
                jugador.descartar_carta(carta)
            else:
                panico = False

    # Funciones para conexion del websocket
    async def connect_game(self, websocket: WebSocket):
        await websocket.accept()
        msg = await websocket.receive_json()
        if "player_id" in msg:
            for p in self.jugadores_en_partida:
                if p.id == msg["player_id"]:
                    jugador = p
            jugador.ws_player = websocket
            if jugador.get_turno():
                await self.mensaje_personal(jugador.id, HABILITADO_ROBAR_CARTA)
        else:
            print("error al conectar jugador")
        self.ws_players_game.append(websocket)
        await self.broadcast_global(CAMBIO_ESTADO_JUEGO)
        await self.broadcast_global(CAMBIO_ESTADO_JUGADOR)

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

    async def mensaje_personal_dict(self, player_id: int, message: dict):
        jugador = self.get_jugador(player_id)
        await jugador.ws_player.send_json(message)
        await jugador.ws_player.send_json("reset")

    def robar_carta_determinacion(self):
        cartas = []
        while len(cartas) < 3:
            if len(self.mazo) == 0:
                random.shuffle(self.mazo_descarte)
                self.mazo = self.mazo_descarte
                self.mazo_descarte = []
            carta_id = self.mazo.pop()
            if carta_id in list(range(89, 109)):
                self.mazo_descarte.append(carta_id)
            else:
                cartas.append({"id": carta_id})
                self.cartas_determinacion.append(carta_id)
        return cartas


def robar_carta(juego: Juego, jugador: JugadorPartida):
    if len(juego.mazo) == 0:
        raise HTTPException(
            status_code=400,
            detail="El mazo esta vacio")
    carta_id = juego.mazo.pop()
    jugador.agregar_carta(carta_id)
    mazo_vacio(juego)
    return carta_id

def mazo_vacio(juego: Juego):
    if len(juego.mazo) == 0:
        print("mezcle el mazo porque no habia cartas")
        random.shuffle(juego.mazo_descarte)
        juego.mazo = juego.mazo_descarte
        juego.mazo_descarte = []

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
