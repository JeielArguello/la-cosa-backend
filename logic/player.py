class JugadorPartida:
    def __init__(self, id: int):
        self.id = id
        self.la_cosa = False
        self.infectado = False
        self.turno_actual = False
        self.posicion = 0
        self.cartas = []

    def set_la_cosa(self):
        self.la_cosa = True

    def get_la_cosa(self):
        return self.la_cosa

    def set_infectado(self):
        self.infectado = True

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
        return self.cartas

    def descartar_carta(self, carta: int):
        return self.cartas.remove(carta)
