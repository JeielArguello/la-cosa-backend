from fastapi import WebSocket
from pony.orm import *
from models.crud import get_name
from models.database import *


class JugadorPartida:
    def __init__(self, id: int):
        self.id = id
        self.muerto = False
        self.la_cosa = False
        self.infectado = False
        self.humano = True
        self.turno_actual = False
        self.posicion = 0
        self.cartas = []
        self.ws_player: WebSocket = None
        self.name = get_name(id)
        self.afectado_seduccion = False

    def get_muerto(self):
        return self.muerto

    def set_muerto(self):
        self.muerto = True

    def set_la_cosa(self):
        self.la_cosa = True

    def get_la_cosa(self):
        return self.la_cosa

    def get_infectado(self):
        return self.infectado

    def get_humano(self):
        return self.humano

    def set_infectado(self):
        self.infectado = True
        self.humano = False

    def get_infectado(self):
        return self.infectado

    def cambiar_turno(self):
        self.turno_actual = not self.turno_actual

    def get_turno(self):
        return self.turno_actual

    def set_posicion(self, posicion: int):
        self.posicion = posicion

    def get_posicion(self):
        return self.posicion

    def agregar_carta(self, carta: int):
        self.cartas.append(carta)

    def get_cartas(self):
        result = []
        for c in self.cartas:
            result.append({'id': c})
        return result

    def descartar_carta(self, carta: int):
        return self.cartas.remove(carta)
