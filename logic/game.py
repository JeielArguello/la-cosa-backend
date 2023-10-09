import random
from logic.deck import deck_es_carta_alejate
from logic.player import JugadorPartida
from fastapi import HTTPException
# from logic.deck import robar_carta
from typing import List


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

        # spawnear jugadores
        for id in jugadores_id:
            jugador = JugadorPartida(id)
            self.jugadores_en_partida.append(jugador)
        # Estados iniciales
        # otorgar posiciones
        for jugador_id in self.jugadores_id:
            self.posiciones.append(jugador_id)
            self.posiciones.append(0)
        # crear mazo
        # elegir la cosa
        # repartir cartas

    def jugar_turno(self):
        for jugador in self.jugadores_en_partida:
            if jugador.get_turno:
                # robar carta
                # robar_carta(self, jugador)

                # # chequear superinfeccion
                # if carta.tipo_de_accion == "Panico":
                #     # aplicar panico
                #     # descartarla
                #     pass
                # else:
                #     jugador.agregar_carta(carta_id)
                # # jugar carta/descartar
                # await accion(accion: str, carta_id_in: int):
                #     if accion == jugar_carta:
                #         aplicar_efecto_accion(carta_id_in):
                #             carta = read_carta(db, carta_id_in)
                # # descartar
                # jugador.descartar_carta(carta_id_in)
                # self.mazo_descarte.append(carta_id_in)
                # # intercambiar
                # intercambiar_cartas(jugador_en_turno: int, jugador_fuera_turno: int):
                #     # await jugador turno
                #     # select carta
                #     # await jugador fuera turno
                #     # select carta
                #     # swap ()
                print(f"turno de {jugador.id}")
                jugador.cambiar_turno()

    def manejar_turnos(self):
        if self.sentido == 1:
            self.turno = (self.turno + 1) % len(self.jugadores_en_partida)
        elif self.sentido == 0:
            self.turno = (self.turno - 1) % len(self.jugadores_en_partida)

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
