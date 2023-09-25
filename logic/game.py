from .player import *
from models.crud import read_carta


class Juego:
    def __init__(self, partida_id: int, cantidad_jugadores: int, creador: int,
                 jugadores_id: list[int]):
        self.partida_id = partida_id
        self.cantidad_jugadores = cantidad_jugadores
        self.creador = creador
        self.jugadores_id = jugadores_id

        self.jugadores_en_partida = []
        self.sentido = 1
        self.turno = -1
        self.mazo = []
        self.mazo_descarte = []
        self.posiciones = []

        # spawnear jugadores
        for id in jugadores_id:
            jugador = JugadorPartida(id)
            self.jugadores_en_partida.append(jugador)

        # Estados iniciales
        # crear mazo
        # elegir la cosa
        # repartir cartas
        # otorgar posiciones

    def jugar_turno(self):
        for jugador in self.jugadores_en_partida:
            if jugador.get_turno:
                # robar carta
                carta_id = self.mazo.pop
                carta = read_carta(carta_id)
                if carta.tipo_de_accion == "Panico":
                    # aplicar panico
                    # descartar
                    # intercambiar
                    pass
                else:
                    jugador.agregar_carta(carta_id)
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
            self.turno = (self.turno+1) % len(self.jugadores_en_partida)
        elif self.sentido == 0:
            self.turno = (self.turno-1) % len(self.jugadores_en_partida)

        jugador = self.jugadores_en_partida[self.turno]
        jugador.cambiar_turno()
        print("manejador turno")

    def jugar_partida(self):
        while 1:
            self.manejar_turnos()
            self.jugar_turno()
            # chequear ganador
            # if hay_ganador:
            #     break
        # notificar resultados
        # finalizar partida
        print("partida")
