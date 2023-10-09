from .database import Carta
from pony.orm import db_session


@db_session
def create_cards():
    if not Carta.exists():
        carta1 = Carta(nombre="La Cosa", numero_jugadores=1,
                       tipo_dorso=0, tipo_de_accion='La cosa', descripcion='')

        carta2 = Carta(
            nombre="Infectado",
            numero_jugadores=4,
            tipo_dorso=0,
            tipo_de_accion='Infectado',
            descripcion='')
        carta3 = Carta(
            nombre="Infectado",
            numero_jugadores=4,
            tipo_dorso=0,
            tipo_de_accion='Infectado',
            descripcion='')
        carta4 = Carta(
            nombre="Infectado",
            numero_jugadores=4,
            tipo_dorso=0,
            tipo_de_accion='Infectado',
            descripcion='')
        carta5 = Carta(
            nombre="Infectado",
            numero_jugadores=4,
            tipo_dorso=0,
            tipo_de_accion='Infectado',
            descripcion='')
        carta6 = Carta(
            nombre="Infectado",
            numero_jugadores=4,
            tipo_dorso=0,
            tipo_de_accion='Infectado',
            descripcion='')
        carta7 = Carta(
            nombre="Infectado",
            numero_jugadores=4,
            tipo_dorso=0,
            tipo_de_accion='Infectado',
            descripcion='')
        carta8 = Carta(
            nombre="Infectado",
            numero_jugadores=4,
            tipo_dorso=0,
            tipo_de_accion='Infectado',
            descripcion='')
        carta9 = Carta(
            nombre="Infectado",
            numero_jugadores=4,
            tipo_dorso=0,
            tipo_de_accion='Infectado',
            descripcion='')
        carta10 = Carta(
            nombre="Infectado",
            numero_jugadores=6,
            tipo_dorso=0,
            tipo_de_accion='Infectado',
            descripcion='')
        carta11 = Carta(
            nombre="Infectado",
            numero_jugadores=6,
            tipo_dorso=0,
            tipo_de_accion='Infectado',
            descripcion='')
        carta12 = Carta(
            nombre="Infectado",
            numero_jugadores=7,
            tipo_dorso=0,
            tipo_de_accion='Infectado',
            descripcion='')
        carta13 = Carta(
            nombre="Infectado",
            numero_jugadores=7,
            tipo_dorso=0,
            tipo_de_accion='Infectado',
            descripcion='')
        carta14 = Carta(
            nombre="Infectado",
            numero_jugadores=8,
            tipo_dorso=0,
            tipo_de_accion='Infectado',
            descripcion='')
        carta15 = Carta(
            nombre="Infectado",
            numero_jugadores=9,
            tipo_dorso=0,
            tipo_de_accion='Infectado',
            descripcion='')
        carta16 = Carta(
            nombre="Infectado",
            numero_jugadores=9,
            tipo_dorso=0,
            tipo_de_accion='Infectado',
            descripcion='')
        carta17 = Carta(
            nombre="Infectado",
            numero_jugadores=10,
            tipo_dorso=0,
            tipo_de_accion='Infectado',
            descripcion='')
        carta18 = Carta(
            nombre="Infectado",
            numero_jugadores=10,
            tipo_dorso=0,
            tipo_de_accion='Infectado',
            descripcion='')
        carta19 = Carta(
            nombre="Infectado",
            numero_jugadores=11,
            tipo_dorso=0,
            tipo_de_accion='Infectado',
            descripcion='')
        carta20 = Carta(
            nombre="Infectado",
            numero_jugadores=11,
            tipo_dorso=0,
            tipo_de_accion='Infectado',
            descripcion='')
        carta21 = Carta(
            nombre="Infectado",
            numero_jugadores=11,
            tipo_dorso=0,
            tipo_de_accion='Infectado',
            descripcion='')

        carta22 = Carta(nombre="Lanzallamas", numero_jugadores=4,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')
        carta23 = Carta(nombre="Lanzallamas", numero_jugadores=4,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')
        carta24 = Carta(nombre="Lanzallamas", numero_jugadores=6,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')
        carta25 = Carta(nombre="Lanzallamas", numero_jugadores=9,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')
        carta26 = Carta(nombre="Lanzallamas", numero_jugadores=11,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')

        carta27 = Carta(nombre="Analisis", numero_jugadores=4,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')
        carta28 = Carta(nombre="Analisis", numero_jugadores=6,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')
        carta29 = Carta(nombre="Analisis", numero_jugadores=9,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')

        carta30 = Carta(nombre="Hacha", numero_jugadores=4,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')
        carta31 = Carta(nombre="Hacha", numero_jugadores=9,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')

        carta32 = Carta(nombre="Sospecha", numero_jugadores=4,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')
        carta33 = Carta(nombre="Sospecha", numero_jugadores=4,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')
        carta34 = Carta(nombre="Sospecha", numero_jugadores=4,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')
        carta35 = Carta(nombre="Sospecha", numero_jugadores=4,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')
        carta36 = Carta(nombre="Sospecha", numero_jugadores=7,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')
        carta37 = Carta(nombre="Sospecha", numero_jugadores=8,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')
        carta38 = Carta(nombre="Sospecha", numero_jugadores=9,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')
        carta39 = Carta(nombre="Sospecha", numero_jugadores=10,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')

        carta40 = Carta(nombre="Whisky", numero_jugadores=4,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')
        carta41 = Carta(nombre="Whisky", numero_jugadores=6,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')
        carta42 = Carta(nombre="Whisky", numero_jugadores=10,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')

        carta43 = Carta(nombre="Determinacion", numero_jugadores=4,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')
        carta44 = Carta(nombre="Determinacion", numero_jugadores=4,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')
        carta45 = Carta(nombre="Determinacion", numero_jugadores=6,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')
        carta46 = Carta(nombre="Determinacion", numero_jugadores=9,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')
        carta47 = Carta(nombre="Determinacion", numero_jugadores=10,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')

        carta48 = Carta(nombre="Vigila tus espaldas", numero_jugadores=4,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')
        carta49 = Carta(nombre="Vigila tus espaldas", numero_jugadores=9,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')

        carta50 = Carta(nombre="Cambio de lugar", numero_jugadores=4,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')
        carta51 = Carta(nombre="Cambio de lugar", numero_jugadores=4,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')
        carta52 = Carta(nombre="Cambio de lugar", numero_jugadores=7,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')
        carta53 = Carta(nombre="Cambio de lugar", numero_jugadores=9,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')
        carta54 = Carta(nombre="Cambio de lugar", numero_jugadores=11,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')

        carta55 = Carta(nombre="Mas vale que corras", numero_jugadores=4,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')
        carta56 = Carta(nombre="Mas vale que corras", numero_jugadores=4,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')
        carta57 = Carta(nombre="Mas vale que corras", numero_jugadores=7,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')
        carta58 = Carta(nombre="Mas vale que corras", numero_jugadores=9,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')
        carta59 = Carta(nombre="Mas vale que corras", numero_jugadores=11,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')

        carta60 = Carta(nombre="Seduccion", numero_jugadores=4,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')
        carta61 = Carta(nombre="Seduccion", numero_jugadores=4,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')
        carta62 = Carta(nombre="Seduccion", numero_jugadores=6,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')
        carta63 = Carta(nombre="Seduccion", numero_jugadores=7,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')
        carta64 = Carta(nombre="Seduccion", numero_jugadores=8,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')
        carta65 = Carta(nombre="Seduccion", numero_jugadores=10,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')
        carta66 = Carta(nombre="Seduccion", numero_jugadores=11,
                        tipo_dorso=0, tipo_de_accion='Accion', descripcion='')

        carta67 = Carta(nombre="Aterrador", numero_jugadores=5,
                        tipo_dorso=0, tipo_de_accion='Defensa', descripcion='')
        carta68 = Carta(nombre="Aterrador", numero_jugadores=6,
                        tipo_dorso=0, tipo_de_accion='Defensa', descripcion='')
        carta69 = Carta(nombre="Aterrador", numero_jugadores=8,
                        tipo_dorso=0, tipo_de_accion='Defensa', descripcion='')
        carta70 = Carta(nombre="Aterrador", numero_jugadores=11,
                        tipo_dorso=0, tipo_de_accion='Defensa', descripcion='')

        carta71 = Carta(nombre="Aqui estoy bien", numero_jugadores=4,
                        tipo_dorso=0, tipo_de_accion='Defensa', descripcion='')
        carta72 = Carta(nombre="Aqui estoy bien", numero_jugadores=6,
                        tipo_dorso=0, tipo_de_accion='Defensa', descripcion='')
        carta73 = Carta(nombre="Aqui estoy bien", numero_jugadores=11,
                        tipo_dorso=0, tipo_de_accion='Defensa', descripcion='')

        carta74 = Carta(nombre="No gracias", numero_jugadores=4,
                        tipo_dorso=0, tipo_de_accion='Defensa', descripcion='')
        carta75 = Carta(nombre="No gracias", numero_jugadores=6,
                        tipo_dorso=0, tipo_de_accion='Defensa', descripcion='')
        carta76 = Carta(nombre="No gracias", numero_jugadores=8,
                        tipo_dorso=0, tipo_de_accion='Defensa', descripcion='')
        carta77 = Carta(nombre="No gracias", numero_jugadores=11,
                        tipo_dorso=0, tipo_de_accion='Defensa', descripcion='')

        carta78 = Carta(nombre="Fallaste", numero_jugadores=4,
                        tipo_dorso=0, tipo_de_accion='Defensa', descripcion='')
        carta79 = Carta(nombre="Fallaste", numero_jugadores=6,
                        tipo_dorso=0, tipo_de_accion='Defensa', descripcion='')
        carta80 = Carta(nombre="Fallaste", numero_jugadores=11,
                        tipo_dorso=0, tipo_de_accion='Defensa', descripcion='')

        carta81 = Carta(nombre="Nada de barbacoas", numero_jugadores=4,
                        tipo_dorso=0, tipo_de_accion='Defensa', descripcion='')
        carta82 = Carta(nombre="Nada de barbacoas", numero_jugadores=6,
                        tipo_dorso=0, tipo_de_accion='Defensa', descripcion='')
        carta83 = Carta(nombre="Nada de barbacoas", numero_jugadores=11,
                        tipo_dorso=0, tipo_de_accion='Defensa', descripcion='')

        carta84 = Carta(
            nombre="Cuarentena",
            numero_jugadores=5,
            tipo_dorso=0,
            tipo_de_accion='Obstaculo',
            descripcion='')
        carta85 = Carta(
            nombre="Cuarentena",
            numero_jugadores=9,
            tipo_dorso=0,
            tipo_de_accion='Obstaculo',
            descripcion='')

        carta86 = Carta(
            nombre="Puerta Atrancada",
            numero_jugadores=4,
            tipo_dorso=0,
            tipo_de_accion='Obstaculo',
            descripcion='')
        carta87 = Carta(
            nombre="Puerta Atrancada",
            numero_jugadores=7,
            tipo_dorso=0,
            tipo_de_accion='Obstaculo',
            descripcion='')
        carta88 = Carta(
            nombre="Puerta Atrancada",
            numero_jugadores=11,
            tipo_dorso=0,
            tipo_de_accion='Obstaculo',
            descripcion='')

        carta89 = Carta(nombre="Cuerdas podridas", numero_jugadores=6,
                        tipo_dorso=1, tipo_de_accion='Panico', descripcion='')
        carta90 = Carta(nombre="Cuerdas podridas", numero_jugadores=9,
                        tipo_dorso=1, tipo_de_accion='Panico', descripcion='')

        carta91 = Carta(nombre="Uno dos", numero_jugadores=5,
                        tipo_dorso=1, tipo_de_accion='Panico', descripcion='')
        carta92 = Carta(nombre="Uno dos", numero_jugadores=9,
                        tipo_dorso=1, tipo_de_accion='Panico', descripcion='')

        carta93 = Carta(nombre="Tres cuatro", numero_jugadores=4,
                        tipo_dorso=1, tipo_de_accion='Panico', descripcion='')
        carta94 = Carta(nombre="Tres cuatro", numero_jugadores=9,
                        tipo_dorso=1, tipo_de_accion='Panico', descripcion='')

        carta95 = Carta(nombre="Es aqui la fiesta", numero_jugadores=5,
                        tipo_dorso=1, tipo_de_accion='Panico', descripcion='')
        carta96 = Carta(nombre="Es aqui la fiesta", numero_jugadores=9,
                        tipo_dorso=1, tipo_de_accion='Panico', descripcion='')

        carta97 = Carta(nombre="Sal de aqui", numero_jugadores=5,
                        tipo_dorso=1, tipo_de_accion='Panico', descripcion='')

        carta98 = Carta(nombre="Olvidadizo", numero_jugadores=4,
                        tipo_dorso=1, tipo_de_accion='Panico', descripcion='')

        carta99 = Carta(nombre="Vuelta y vuelta", numero_jugadores=4,
                        tipo_dorso=1, tipo_de_accion='Panico', descripcion='')
        carta100 = Carta(nombre="Vuelta y vuelta", numero_jugadores=9,
                         tipo_dorso=1, tipo_de_accion='Panico', descripcion='')

        carta101 = Carta(nombre="No podemos ser amigos", numero_jugadores=7,
                         tipo_dorso=1, tipo_de_accion='Panico', descripcion='')
        carta102 = Carta(nombre="No podemos ser amigos", numero_jugadores=9,
                         tipo_dorso=1, tipo_de_accion='Panico', descripcion='')

        carta103 = Carta(nombre="Cita a ciegas", numero_jugadores=4,
                         tipo_dorso=1, tipo_de_accion='Panico', descripcion='')
        carta104 = Carta(nombre="Cita a ciegas", numero_jugadores=9,
                         tipo_dorso=1, tipo_de_accion='Panico', descripcion='')

        carta105 = Carta(nombre="Ups", numero_jugadores=10,
                         tipo_dorso=1, tipo_de_accion='Panico', descripcion='')

        carta106 = Carta(nombre="Que quede entre nosotros", numero_jugadores=7,
                         tipo_dorso=1, tipo_de_accion='Panico', descripcion='')
        carta107 = Carta(nombre="Que quede entre nosotros", numero_jugadores=9,
                         tipo_dorso=1, tipo_de_accion='Panico', descripcion='')

        carta108 = Carta(nombre="Revelaciones", numero_jugadores=8,
                         tipo_dorso=1, tipo_de_accion='Panico', descripcion='')
