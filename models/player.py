from typing import Tuple
from fastapi import WebSocket
from pony.orm import *
from models.crud import get_name ,get_id_avatar
from models.database import *


class JugadorPartida:
    def __init__(self, id: int):
        self.id = id
        self.id_avatar = get_id_avatar(id)
        self.muerto = False
        self.la_cosa = False
        self.infectado = False
        self.humano = True
        self.turno_actual = False
        self.cuarentena = (False,0) 
        self.posicion = 0
        self.cartas = []
        self.ws_player: WebSocket = None
        self.name = get_name(id)
        self.efecto_seduccion = False
        self.efecto_fallaste = False

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
    
    def set_cuartena(self):
        self.cuarentena = (True, 2)

    def get_cuartena(self):
        return self.cuarentena[0]

    def pop_cuarentena(self):
        if (self.cuarentena[1] > 0):
            self.cuarentena = (True,self.cuarentena[1] - 1)
        if (self.cuarentena[1] == 0):
            self.cuarentena = (False, 0)

    def remove_cuartena(self):
        self.cuarentena = (False, 0)

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
    
    def set_efecto_seduccion(self):
        self.efecto_seduccion = True

    def get_efecto_seduccion(self):
        return self.efecto_seduccion
    
    def remove_efecto_seduccion(self):
        self.efecto_seduccion = False
    
    def set_efecto_fallaste(self):
        self.efecto_fallaste = True

    def get_efecto_fallaste(self):
        return self.efecto_fallaste
    
    def remove_efecto_fallaste(self):
        self.efecto_fallaste = False
    
    def check_puede_anular_el_intercambio(self):
        mano = self.get_cartas()
        listaDeCardsIdQueAnulanIntercambio = [67,68,69,70,74,75,76,77,78,79,80]
        puedeAnularIntercambio = False
        for card in mano: 
            if card["id"] in listaDeCardsIdQueAnulanIntercambio:
                puedeAnularIntercambio = True 
            
        return puedeAnularIntercambio
