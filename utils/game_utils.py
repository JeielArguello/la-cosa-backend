
from logic.defense_effects import defensa_aqui_estoy_bien, defensa_fallaste, defensa_nada_de_barbacoas, defensa_no_gracias, defense_aterrador
from logic.obstacle_effects import play_puerta_atrancada, play_cuarentena
from utils.action_utils import get_jugador
from fastapi import HTTPException
from logic.panic_effects import *
from models.crud import get_name, read_carta, get_dorso_carta
from models.database_utils import get_jugadores_match
from models.game import Juego, mazo_vacio
from models.player import JugadorPartida
from logic.action_effects import *
from models.constants import *


global_juegos: list[Juego] = []


def get_status_game(juego: Juego):
    posiciones = juego.posiciones
    sentido = juego.sentido
    jugadores = get_jugadores_match(juego.posiciones)
    list_jugadores = []
    for j in jugadores:
        jugador = juego.get_jugador(j['id'])
        list_jugadores.append({'id': j['id'],
                               'nombre': j['nombre'],
                               'cuarentena': jugador.get_cuartena(),
                               'id_avatar': j['id_avatar']})
    carta = read_carta(juego.mazo[-1])
    id_player_turno = juego.get_jugador_en_turno().id
    response = {'posiciones': posiciones,
                'jugadores': list_jugadores,
                'sentido': sentido,
                'tipo_dorso': carta.tipo_dorso,
                'id_player_turno': id_player_turno}
    return response


def get_global_juego(match_id: int) -> Juego:
    result = None
    for juego in global_juegos:
        if juego.partida_id == match_id:
            result = juego
    if (result is None):
        raise HTTPException(
            status_code=400, detail="No se pudo acceder al juego")
    return result


def delete_global_juego(match_id):
    result = None
    for juego in global_juegos:
        if juego.partida_id == match_id:
            result = juego
    if (result is None):
        raise HTTPException(
            status_code=400, detail="No se puedo borrar el juego")
    global_juegos.remove(result)


def get_status_player(juego: Juego, player_id: int):
    jugador = None
    for j in juego.jugadores_en_partida:
        if j.id == player_id:
            jugador = j
    if jugador is None:
        raise HTTPException(
            status_code=400,
            detail="El jugador no se encuentra en la partida")
    mano = jugador.get_cartas()
    muerto = jugador.muerto
    la_cosa = jugador.la_cosa
    humano = jugador.humano
    infectado = jugador.infectado
    response = {'mano': mano, 'muerto': muerto, 'la_cosa': la_cosa,
                'humano': humano, 'infectado': infectado}
    return response


def check_ganador(juego: Juego) -> bool:
    first = check_la_cosa_eliminada(juego)
    second = check_la_cosa_sola_viva(juego)
    result = first or second
    return result


def finalizar_juego(juego: Juego):
    la_cosa = []
    humanos_vivos = []
    humanos_muertos = []
    infectados_vivos = []
    infectados_muertos = []
    for j in juego.jugadores_en_partida:
        name = get_name(j.id)
        if j.get_la_cosa():
            la_cosa.append(name)
        if j.get_infectado() and not j.get_muerto():
            infectados_vivos.append(name)
        if j.get_infectado() and j.get_muerto():
            infectados_muertos.append(name)
        if j.get_humano() and not j.get_muerto():
            humanos_vivos.append(name)
        if j.get_humano() and j.get_muerto():
            humanos_muertos.append(name)

    if check_la_cosa_eliminada(juego):
        return {
            'message': 'La cosa fue eliminada, Ganan los Humanos.',
            'winners': humanos_vivos,
            'losers': la_cosa + infectados_vivos + infectados_muertos + humanos_muertos}
    elif check_no_humanos_no_eliminados(juego):
        return {
            'message': 'Todos fueron infectados, Gana La Cosa.',
            'winners': la_cosa,
            'losers': infectados_vivos + infectados_muertos + humanos_vivos + humanos_muertos}
    elif check_no_humanos(juego):
        return {
            'message': 'Ganan La Cosa y Los Infectados.',
            'winners': la_cosa + infectados_vivos,
            'losers': humanos_vivos + humanos_muertos + infectados_muertos}
    elif not check_no_humanos(juego):
        return {
            'message': 'La cosa decreto mal el fin de la partida, Ganan los Humanos.',
            'winners': humanos_vivos,
            'losers': la_cosa + infectados_vivos + humanos_muertos + infectados_muertos}
    elif check_la_cosa_sola_viva(juego):
        return {
            'message': 'La cosa es la ultima en pie, Gana la Cosa.',
            'winners': la_cosa,
            'losers': humanos_vivos + infectados_vivos + humanos_muertos + infectados_muertos}
    else:
        raise HTTPException(
            status_code=400, detail="No hay ganadores.")


def check_la_cosa_eliminada(juego: Juego) -> bool:
    la_cosa_eliminada = True
    for j in juego.jugadores_en_partida:
        if j.get_la_cosa() and not j.get_muerto():
            la_cosa_eliminada = False
    return la_cosa_eliminada


async def mostrar_cartas_cuarentena(jugador: JugadorPartida, card_id: int, juego: Juego, etapa: int):
    if jugador.get_cuartena():
        if etapa == 1:  # robar
            await juego.broadcast_global({"carta_id": 84,
                                          "jugador_obj": get_name(jugador.id),
                                          "mensaje": "El jugador " + jugador.name + " que está en cuarentena robó una carta.",
                                          "cartaMostrar": [{"id": card_id}]})
        elif etapa == 2:  # descartar
            await juego.broadcast_global({"carta_id": 84,
                                          "jugador_obj": get_name(jugador.id),
                                          "mensaje": "El jugador " + jugador.name + " que está en cuarentena descarto una carta.",
                                          "cartaMostrar": [{"id": card_id}]})
        elif etapa == 3:  # intercambio
            await juego.broadcast_global({"carta_id": 84,
                                          "jugador_obj": get_name(jugador.id),
                                          "mensaje": "El jugador " + jugador.name + " que está en cuarentena intercambio una carta.",
                                          "cartaMostrar": [{"id": card_id}]})


async def mostrar_cartas_cuarentena_ambos(jugador: JugadorPartida, card_id: int, jugador_obj: JugadorPartida, card_id_obj: int, juego: Juego):
    if jugador.get_cuartena() and jugador_obj.get_cuartena():
        await juego.broadcast_global({"carta_id": 84,
                                      "jugador_obj": "Los jugadores " + get_name(jugador.id) + " y " + get_name(jugador_obj.id),
                                      "mensaje": jugador.name + " y " + jugador_obj.name + " que estan en cuarentena intercambiaron cartas.",
                                      "cartaMostrar": [{"id": card_id}, {"id": card_id_obj}]})


def check_no_humanos(juego: Juego) -> bool:
    no_humanos = True
    for j in juego.jugadores_en_partida:
        if j.get_humano() and not j.get_muerto():
            no_humanos = False
    return no_humanos


def check_no_humanos_no_eliminados(juego: Juego) -> bool:
    no_humanos = True
    no_muertos = True
    for j in juego.jugadores_en_partida:
        if j.get_humano() and not j.get_muerto():
            no_humanos = False
        if j.get_muerto():
            no_muertos = False
    return no_humanos and no_muertos


def check_la_cosa_sola_viva(juego: Juego) -> bool:
    la_cosa_sola_viva = True
    for j in juego.jugadores_en_partida:
        if not j.get_la_cosa() and not j.get_muerto():
            la_cosa_sola_viva = False
    return la_cosa_sola_viva


async def jugar_la_carta(
        juego: Juego,
        card_id: int,
        player_objective: int,
        player_orig: int):
    if card_id <= 88:
        validar_jugada(juego, card_id, player_objective, player_orig)

    if card_id in [22, 23, 24, 25, 26]:
        msg = play_lanzallamas(player_orig, player_objective, juego)
        await juego.broadcast_global({"carta_id": card_id,
                                     "mensaje": msg["mensaje"]})
        await juego.mensaje_personal(player_objective, CAMBIO_ESTADO_JUGADOR)

    elif card_id in [27, 28, 29]:
        msg = play_analisis(juego, player_orig, player_objective)
        await juego.broadcast_global({"carta_id": card_id,
                                      "mensaje": msg["mensaje"]})
        await juego.mensaje_personal(player_orig,
                                     {"carta_id": card_id,
                                      "jugador_obj": get_name(player_objective),
                                      "mensaje": msg["mensaje"],
                                      "cartaMostrar": msg["cartaMostrar"]})

    elif card_id in [30, 31]:
        msg = play_hacha(player_orig, player_objective, juego)
        await juego.broadcast_global({"carta_id": card_id,
                                      "mensaje": msg["mensaje"]})
        await juego.broadcast_global(CAMBIO_ESTADO_JUEGO)

    elif card_id in [32, 33, 34, 35, 36, 37, 38, 39]:
        msg = play_sospecha(player_orig, player_objective, juego)
        await juego.broadcast_global({"carta_id": card_id,
                                      "mensaje": msg["mensaje"]})
        await juego.mensaje_personal(player_orig, {"carta_id": card_id,
                                                   "mensaje": msg["mensaje"],
                                                   "cartaMostrar": msg["cartaMostrar"],
                                                   "jugador_obj": get_name(player_objective)})

    elif card_id in [40, 41, 42]:
        msg = play_whisky(player_orig, juego, card_id)
        await juego.broadcast_global({"carta_id": card_id,
                                      "mensaje": msg["mensaje"],
                                      "cartaMostrar": msg["cartaMostrar"],
                                      "jugador_obj": get_name(player_objective)})

    elif card_id in [43, 44, 45, 46, 47]:
        msg = play_determinacion(juego, player_orig)
        mensaje = {
            "carta_especial": {
                "tipo_carta": "Determinacion",
                "cartas": msg["cartas"],
                "jugadores": []
            }
        }
        await juego.mensaje_personal(player_orig, mensaje)
        await juego.broadcast_global({
            "carta_id": card_id,
            "mensaje": msg["mensaje"]
        })

    elif card_id in [48, 49]:
        play_vigila_tus_espaldas(juego)
        name_player = get_name(player_orig)
        msg = {"carta_id": card_id,
               "mensaje": name_player + " jugó carta vigila tus espaldas."}
        #await juego.broadcast_global()
        await juego.broadcast_global(CAMBIO_ESTADO_JUEGO)
        jugador = juego.get_jugador(player_orig)
        juego.agregar_log(msg["mensaje"])
        juego.agregar_log(jugador.name + " cambió  el sentido del juego.")

    elif card_id in [50, 51, 52, 53, 54]:
        msg = play_cambio_de_lugar(juego, player_orig, player_objective)
        await juego.broadcast_global({"carta_id": card_id,
                                      "mensaje": msg["mensaje"]})

    elif card_id in [55, 56, 57, 58, 59]:
        msg = play_mas_vale_que_corras(player_orig, player_objective, juego)
        await juego.broadcast_global({"carta_id": card_id,
                                      "mensaje": msg["mensaje"]})
        await juego.broadcast_global(CAMBIO_ESTADO_JUEGO)

    elif card_id in [60, 61, 62, 63, 64, 65, 66]:
        msg = play_seduccion(juego, player_orig, player_objective)
        await juego.broadcast_global({"carta_id": card_id,
                                     "mensaje": msg["mensaje"]})

    elif card_id in [84, 85]:
        msg = play_cuarentena(player_orig, player_objective, juego)
        await juego.broadcast_global({"carta_id": card_id,
                                     "mensaje": msg["mensaje"]})
        await juego.broadcast_global(CAMBIO_ESTADO_JUEGO)

    elif card_id in [86, 87, 88]:
        msg = play_puerta_atrancada(juego, player_orig, player_objective)
        await juego.broadcast_global({"carta_id": card_id,
                                     "mensaje": msg["mensaje"]})
        await juego.broadcast_global(CAMBIO_ESTADO_JUEGO)

    elif card_id in [89, 90]:
        msg = play_cuerdas_podridas(player_orig, juego)
        await juego.broadcast_global({"carta_id": card_id,
                                     "mensaje": msg["mensaje"]})

    elif card_id in [93, 94]:
        msg = play_tres_cuatro(player_orig, juego)
        await juego.broadcast_global({"carta_id": card_id,
                                     "mensaje": msg["mensaje"]})

    elif card_id in [95, 96]:
        msg = play_es_aqui_la_fiesta(player_orig, juego)
        await juego.broadcast_global({"carta_id": card_id,
                                     "mensaje": msg["mensaje"]})

    elif card_id in [105]:
        msg = play_ups(player_orig, juego)
        await juego.broadcast_global({"carta_id": card_id,
                                      "mensaje": msg["mensaje"],
                                      "cartaMostrar": msg["cartaMostrar"],
                                      "jugador_obj": get_name(player_objective)})
    elif card_id in [107, 106]:
        msg = play_que_quede_entre_nosotros(
            player_orig, player_objective, juego, card_id)
        await juego.mensaje_personal(player_objective, {"carta_id": card_id,
                                                        "mensaje": msg["mensaje"],
                                                        "cartaMostrar": msg["cartaMostrar"]})
    else:
        pass


async def defenderse_de_intercambio(
        juego: Juego,
        card_id: int,
        jugador_orig: JugadorPartida,
        jugador_atacante: JugadorPartida):

    if card_id in [67, 68, 69, 70]:
        msg = defense_aterrador(juego, jugador_orig, jugador_atacante, card_id)
        await juego.mensaje_personal(jugador_orig.id,
                                     {"carta_id": card_id,
                                      "jugador_obj": get_name(jugador_atacante.id),
                                      "mensaje": msg["mensaje"],
                                      "cartaMostrar": msg["cartaMostrar"]})
    elif card_id in [71, 72, 73]:
        carta_ataque = juego.solicitud_ataque.carta_atacante
        nombre_ataque = get_name_carta(carta_ataque)
        msg = defensa_aqui_estoy_bien(
            juego, jugador_orig, jugador_atacante, card_id, nombre_ataque)
        await juego.broadcast_global(
            {"carta_id": card_id,
                "mensaje": msg["mensaje"]
             }
        )
    elif card_id in [74, 75, 76, 77]:
        msg = defensa_no_gracias(
            juego, jugador_orig, jugador_atacante, card_id)
        await juego.broadcast_global(
            {"carta_id": card_id,
                "jugador_obj": get_name(jugador_atacante.id),
                "mensaje": msg["mensaje"]
             }
        )
    elif card_id in [78, 79, 80]:
        msg = await defensa_fallaste(juego, jugador_orig, jugador_atacante, card_id)
        await juego.broadcast_global(
            {"carta_id": card_id,
                "jugador_obj": get_name(jugador_atacante.id),
                "mensaje": msg["mensaje"]
             }
        )
    elif card_id in [81, 82, 83]:
        msg = defensa_nada_de_barbacoas(
            juego, jugador_orig, jugador_atacante, card_id)
        await juego.broadcast_global(
            {"carta_id": card_id,
                "mensaje": msg["mensaje"]
             }
        )
    else:
        pass


def validar_jugada(juego: Juego,
                   card_id: int,
                   player_objective: int,
                   player_orig: int):
    if player_orig not in juego.posiciones:
        raise HTTPException(
            status_code=400, detail="Atacante no esta en el juego")
    if player_objective not in juego.posiciones:
        raise HTTPException(
            status_code=400, detail="Objetivo no esta en el juego")
    for j in juego.jugadores_en_partida:
        if player_orig == j.id:
            jugador = j
    if not (card_id in jugador.cartas):
        raise HTTPException(
            status_code=400, detail="El jugador no posee esta carta")


def finalizar_partida(juego: Juego):
    if len(juego.jugadores_en_partida) == 1:
        ganador = juego.jugadores_en_partida.pop()
        ganador_id = ganador.id
        return {"mensaje": "La partida ha finalizado", "ganador": ganador_id}
    elif len(juego.jugadores_en_partida) == 0:
        return {"mensaje": "partida sin jugadores", "ganador": 0}
    else:
        return {"mensaje": "La partida aún no ha finalizado", "ganador": 0}


def descartar_carta(card_id: int, player_id: int, juego: Juego):
    validar_carta(card_id, player_id, juego)
    juego.mazo_descarte.append(card_id)
    jugador = get_jugador(player_id, juego)
    jugador.descartar_carta(card_id)


def agregar_carta_determinacion(card_id: int, player_id: int, juego: Juego):
    jugador = get_jugador(player_id, juego)
    jugador.agregar_carta(card_id)
    juego.cartas_determinacion.remove(card_id)

    for c in juego.cartas_determinacion:
        juego.mazo_descarte.append(c)

    juego.cartas_determinacion = []


def validar_carta(card_id: int, player_id: int, juego: Juego):
    jugador = get_jugador(player_id, juego)
    if not (card_id in jugador.cartas):
        raise HTTPException(
            status_code=400, detail="El jugador no posee esta carta")


def check_turno(jugador: JugadorPartida):
    if not jugador.get_turno():
        raise HTTPException(
            status_code=400, detail="No es el turno del jugador.")


def check_la_cosa(jugador: JugadorPartida):
    if not jugador.get_la_cosa():
        raise HTTPException(
            status_code=400, detail="El jugador no es la cosa.")


def check_cantidad_cartas(jugador: JugadorPartida):
    if len(jugador.cartas) == 5:
        raise HTTPException(
            status_code=400,
            detail="No puedes tener mas de 5 cartas en la mano.")


def check_objetive_is_next(proximo_jugador: JugadorPartida, juego: Juego):
    if juego.sentido == 1:
        turnoaux = (juego.turno + 2) % len(juego.posiciones)
    elif juego.sentido == -1:
        turnoaux = (juego.turno - 2) % len(juego.posiciones)
    if proximo_jugador.id != juego.posiciones[turnoaux]:
        raise HTTPException(
            status_code=400, detail="El jugador objetivo no es el proximo en jugar.")


def check_obstaculo(atacante_id: int, objetivo_id: int, juego: Juego):
    indice_posicion_intermedia = juego.get_posicion_intermedia(
        objetivo_id, atacante_id)
    validar_obstaculo(indice_posicion_intermedia, juego)


def is_obstaculo(atacante_id, objetivo_id, juego: Juego):
    indice_posicion_intermedia = juego.get_posicion_intermedia(
        objetivo_id, atacante_id)
    objetivo = get_jugador(objetivo_id, juego)
    hay_obstaculo = False
    if juego.posiciones[indice_posicion_intermedia] != 0 or objetivo.get_cuartena():
        hay_obstaculo = True

    return hay_obstaculo


def is_superinfeccion(jugador: JugadorPartida):
    cartas = jugador.get_cartas()

    superinfeccion = not jugador.get_infectado()
    for c in cartas:
        if c["id"] in range(2, 21):
            superinfeccion = True and superinfeccion
        else:
            superinfeccion = False
    return superinfeccion


async def eliminar_jugador_superinfeccion(jugador: JugadorPartida, juego: Juego):
    cartas = jugador.get_cartas()

    jugador.set_muerto()
    jugador.remove_efecto_seduccion()
    jugador.remove_efecto_fallaste()
    indice_jugador = juego.posiciones.index(jugador.id)
    if indice_jugador == juego.turno:
        juego.terminar_turno()
        juego.avanzar_turno()
    del juego.posiciones[indice_jugador]
    if juego.posiciones[indice_jugador] == "p":
        indiceaux = (indice_jugador - 1) % len(juego.posiciones)
        juego.posiciones[indiceaux] = "p"
        del juego.posiciones[indice_jugador]
    else:
        del juego.posiciones[indice_jugador]
    juego.agregar_log("El jugador " + jugador.name +
                      " murió por una superinfeccion.")
    await juego.broadcast_global(CAMBIO_ESTADO_JUEGO)
    await juego.mensaje_personal(jugador.id, CAMBIO_ESTADO_JUGADOR)
    await juego.broadcast_global({"carta_id": 2,
                                  "jugador_obj": jugador.name,
                                  "mensaje": "El jugador " + jugador.name + " murió por una superinfeccion.",
                                  "cartaMostrar": cartas})
    ganador = check_ganador(juego)
    if ganador:
        await juego.broadcast_global(PARTIDA_FINALIZADA)


async def check_superinfeccion(juego: Juego):
    for j in juego.jugadores_en_partida:
        if j.id in juego.posiciones and is_superinfeccion(j):
            await eliminar_jugador_superinfeccion(j, juego)


def is_card_defense(card_id):
    is_card_defense = card_id in range(67, 83)
    return is_card_defense


def is_fallaste(card_id):
    is_fallaste = card_id in [78, 79, 80]
    return is_fallaste


def is_lanzallama(card_id: int):
    lanzallama = card_id in [22, 23, 24, 25, 26]
    return lanzallama


def is_hacha(card_id: int):
    hacha = card_id in [30, 31]
    return hacha


def is_seduccion(card_id):
    is_seduccion = card_id in [60, 61, 62, 63, 64, 65, 66]
    return is_seduccion


def check_carta_habilitada(
        card_id: int,
        jugador_orig: JugadorPartida,
        jugador_objetivo: JugadorPartida):
    if card_id == 1:
        raise HTTPException(
            status_code=400, detail="No puedes descartar la carta la cosa.")
    mano = jugador_orig.get_cartas()
    cantidad_cartas_infectados = 0
    for c in mano:
        if is_infectado(c["id"]):
            cantidad_cartas_infectados = cantidad_cartas_infectados+1
    if jugador_orig.get_infectado() and cantidad_cartas_infectados < 2 and is_infectado(card_id):
        raise HTTPException(
            status_code=400, detail="No puedes descartar la unica carta de infectado que tienes.")

    if not jugador_orig.get_la_cosa() and not jugador_orig.get_infectado() and is_infectado(card_id):
        raise HTTPException(
            status_code=400, detail="No puedes intercambiar una carta de infectado si no eres la cosa ni infectado.")

    if jugador_orig.get_infectado() and not jugador_objetivo.get_la_cosa() and is_infectado(card_id):
        raise HTTPException(
            status_code=400, detail="No puedes intercambiar una carta de infectado si no eres la cosa.")


def check_posibilidad_defensa(card_id: int, juego: Juego):
    if card_id != 0:
        defensa = juego.solicitud_ataque
        carta_ataque = defensa.carta_atacante
        # Seduccion && Aterrador || No, gracias || Fallaste
        if carta_ataque in [60, 61, 62, 63, 64, 65, 66] and card_id not in [67, 68, 69, 70, 74, 75, 76, 77, 78, 79, 80]:
            raise HTTPException(
                status_code=400,
                detail="Esta carta no puede defenderte.")
        # Cambio de lugar || Más vale que corras && Aquí estoy bien
        # Anula cambio de lugar y mas vale que corras
        elif carta_ataque in [50, 51, 52, 53, 54, 55, 56, 57, 58, 59] and card_id not in [71, 72, 73]:
            raise HTTPException(
                status_code=400,
                detail="Esta carta no puede defenderte.")
        # Lanzallamas && Nada de barbacoas
        # Anula lanzallamas
        elif carta_ataque in [22, 23, 24, 25, 26] and card_id not in [81, 82, 83]:
            raise HTTPException(
                status_code=400,
                detail="Esta carta no puede defenderte.")


def check_puedo_defender(
        juego: Juego,
        card_id: int,
        player_objective: int,
        player_orig: int):
    jugador = get_jugador(player_objective, juego)
    mano = set(jugador.cartas)
    # Seduccion && Aterrador || No, gracias || Fallaste
    # Anula intercambio y Mirar carta a intercambiar
    if card_id in [60, 61, 62, 63, 64, 65, 66] and (
            set(mano) & set([67, 68, 69, 70, 74, 75, 76, 77, 78, 79, 80])):
        return True
    # Cambio de lugar || Más vale que corras && Aquí estoy bien
    # Anula cambio de lugar y mas vale que corras
    elif card_id in [50, 51, 52, 53, 54, 55, 56, 57, 58, 59] and (set(mano) & set([71, 72, 73])):
        return True
    # Lanzallamas && Nada de barbacoas
    # Anula lanzallamas
    elif card_id in [22, 23, 24, 25, 26] and (set(mano) & set([81, 82, 83])):
        return True
    else:
        return False


def is_infectado(card_id):
    infectado = card_id in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
                            17, 18, 19, 20, 21]
    return infectado


def is_vuelta_y_vuelta(card_id):
    vuelta_y_vuelta = card_id in [99, 100]
    return vuelta_y_vuelta

def is_sal_de_aqui(card_id):
    sal_de_aqui = card_id in [97]
    return sal_de_aqui

def is_uno_dos(card_id):
    uno_dos = card_id in [91, 92]
    return uno_dos

def is_no_podemos_ser_amigos(card_id):
    no_podemos_ser_amigos = card_id in [101, 102]
    return no_podemos_ser_amigos


def is_olvidadizo(card_id):
    olvidadizo = card_id in [98]
    return olvidadizo


def is_cita_a_ciegas(card_id):
    cita_a_ciegas = card_id in [103, 104]
    return cita_a_ciegas

def is_que_quede_entre_nosotros(card_id):
    is_qqen = card_id in [106, 107]
    return is_qqen

def is_panico_no_cambio_estado(card_id):
    panico_no_cambio_estado = is_vuelta_y_vuelta(card_id) or is_sal_de_aqui(card_id) or is_uno_dos(card_id) or is_no_podemos_ser_amigos(card_id) or is_olvidadizo(card_id) or is_cita_a_ciegas(card_id) or is_que_quede_entre_nosotros(card_id)
    return panico_no_cambio_estado


def crear_mensaje_de_ataque(jugador: JugadorPartida, card_id: int):
    carta_name = get_name_carta(card_id)
    mensaje = f"El jugador {jugador.name} jugó {carta_name} contra ti. Quieres defenderte?"
    return mensaje


def check_carta_panico(juego: Juego):
    carta_id = juego.mazo[len(juego.mazo) - 1]
    dorso = get_dorso_carta(carta_id)
    return dorso == 1


async def jugar_panico(carta: int, juego: Juego):
    # cartas cambio de estado
    if carta in [89, 90, 93, 94, 95, 96, 105]:
        jugador_en_turno_id = juego.posiciones[juego.turno]
        await jugar_la_carta(juego, carta, jugador_en_turno_id, jugador_en_turno_id)
    # seleccionar carta
    elif carta in [91, 92]:
        jugador_turno = juego.get_jugador_en_turno()
        index = juego.posiciones.index(jugador_turno.id)
        index_izquierda = (index-6) % len(juego.posiciones)
        index_derecha = (index+6) % len(juego.posiciones)
        jugador_izquieda = juego.get_jugador(
            juego.posiciones[index_izquierda])
        jugador_derecha = juego.get_jugador(
            juego.posiciones[index_derecha])
        if len(juego.posiciones) >= 8 and not jugador_izquieda.get_cuartena() and not jugador_derecha.get_cuartena():
            msg = {
                "carta_especial": {
                    "tipo_carta": "Uno,dos",
                    "cartas": [],
                    "jugadores": [{"nombre": jugador_izquieda.name, "id": jugador_izquieda.id, "avatar": jugador_izquieda.id_avatar},
                                  {"nombre": jugador_derecha.name, "id": jugador_derecha.id, "avatar": jugador_derecha.id_avatar}]
                }
            }
            await juego.mensaje_personal(jugador_turno.id, msg)
        elif len(juego.posiciones) >= 8 and not jugador_izquieda.get_cuartena() and jugador_derecha.get_cuartena():
            msg = play_uno_dos(jugador_turno.id, jugador_izquieda.id, juego)
            await juego.mensaje_personal(jugador_izquieda.id, {"carta_id": 91,
                                                               "mensaje": msg["mensaje"],
                                                               "cartaMostrar": []})
            await juego.broadcast_global("C")
            await juego.mensaje_personal(jugador_turno.id, "G")
        elif len(juego.posiciones) >= 8 and jugador_izquieda.get_cuartena() and not jugador_derecha.get_cuartena():
            msg = play_uno_dos(jugador_turno.id, jugador_derecha.id, juego)
            await juego.mensaje_personal(jugador_derecha.id, {"carta_id": 91,
                                                              "mensaje": msg["mensaje"],
                                                              "cartaMostrar": []})
            await juego.broadcast_global("C")
            await juego.mensaje_personal(jugador_turno.id, "G")
        elif len(juego.posiciones) >= 8 and jugador_izquieda.get_cuartena() and jugador_derecha.get_cuartena():
            msg1 = {
                "mensaje": jugador_turno.name + " jugó la carta Uno,Dos..., pero como los posibles objetivos entan en cuarentena no tiene efecto."}
            msg2 = {"mensaje": "Se jugó una carta de panico, pero no tuvo efecto."}
            juego.agregar_log(msg2["mensaje"])
            await juego.broadcast_global(
                {"carta_id": carta,
                    "mensaje": msg1["mensaje"]
                 })
        elif len(juego.posiciones) < 8:
            msg1 = {
                "mensaje": jugador_turno.name + " jugó la carta Uno,Dos..., pero como hay menos de 4 jugadores no tiene efecto."}
            msg2 = {"mensaje": "Se jugó una carta de panico, pero no tuvo efecto."}
            juego.agregar_log(msg2["mensaje"])
            await juego.broadcast_global(
                {"carta_id": carta,
                    "mensaje": msg1["mensaje"]
                 })
    
    elif carta in [103, 104]:  # cita a ciegas
        jugador_en_turno_id = juego.posiciones[juego.turno]
        jugador_en_turno = juego.get_jugador(jugador_en_turno_id)
        mano = jugador_en_turno.get_cartas()
        msg = {"carta_especial": {
            "tipo_carta": "Cita a ciegas",
            "cartas": mano,
            "jugadores": []
        }
        }
        await juego.mensaje_personal(jugador_en_turno_id, msg)

    # seleccionar jugador
    elif carta in [106, 107]:  # que quede entre nosotros.
        jugador_turno = juego.get_jugador_en_turno()
        jugador_turno_id = jugador_turno.id
        jug_sig_turno = juego.get_jugador_siguiente_turno()
        jug_ant_turno = juego.get_jugador_anterior_turno()
        jug_sig_turno_id = jug_sig_turno.id
        jug_sig_turno_nombre = jug_sig_turno.name
        jug_ant_turno_id = jug_ant_turno.id
        jug_ant_turno_nombre = jug_ant_turno.name

        msg = {
            "carta_especial": {
                "tipo_carta": "Que quede entre nosotros",
                "cartas": [],
                "jugadores": [{"nombre": jug_sig_turno_nombre, "id": jug_sig_turno_id},
                              {"nombre": jug_ant_turno_nombre, "id": jug_ant_turno_id}]
            }
        }
        await juego.mensaje_personal(jugador_turno_id, msg)

    elif carta in [103, 104]:  # cita a ciegas
        jugador_en_turno_id = juego.posiciones[juego.turno]
        jugador_en_turno = juego.get_jugador(jugador_en_turno_id)
        mano = jugador_en_turno.get_cartas()
        msg = {"carta_especial": {
            "tipo_carta": "Cita a ciegas",
            "cartas": mano,
            "jugadores": []
        }
        }
        await juego.mensaje_personal(jugador_en_turno_id, msg)

    # seleccionar intercambio
    elif is_vuelta_y_vuelta(carta):
        jugador_turno = juego.get_jugador_en_turno()
        juego.iniciar_vuelta_y_vuelta(jugador_turno)
        cartas = jugador_turno.get_cartas()
        msg = {
            "carta_especial": {
                "tipo_carta": "Vuelta y vuelta",
                "cartas": cartas,
                "jugadores": []
            }
        }
        await juego.mensaje_personal(jugador_turno.id, msg)
        juego.agregar_log(jugador_turno.name +
                          " jugó la carta Vuelta y Vuelta")
    elif carta in [101, 102]:
        pass

    # olvidadizo
    elif carta in [98]:
        jug_turno = juego.get_jugador_en_turno()
        jug_turno_id = jug_turno.id
        if jug_turno.get_la_cosa():
            msg = {"carta_id": 98,
                   "mensaje": jug_turno.name + " robó carta de Pánico Olvidadizo."
                   }
            play_olvidadizo(juego, jug_turno_id, 1)
            await juego.mensaje_personal(jug_turno_id, msg)
            await juego.mensaje_personal(jug_turno_id, CAMBIO_ESTADO_JUGADOR)
            jugador_proximo = juego.get_jugador_siguiente_turno()

            if (not jugador_proximo.get_muerto() and juego.is_obstaculo(jug_turno.id, jugador_proximo.id)) or is_superinfeccion(jug_turno):
                juego.terminar_turno()
                juego.avanzar_turno()

                await juego.mensaje_personal(jugador_proximo.id, HABILITADO_ROBAR_CARTA)
                await check_superinfeccion(juego)

            else:
                await juego.mensaje_personal(jug_turno.id, HABILITADO_INTERCAMBIO)

        else:
            cartas = jug_turno.get_cartas()
            msg = {
                "carta_especial": {
                    "tipo_carta": "Olvidadizo",
                    "cartas": cartas,
                    "jugadores": []
                }
            }
            await juego.mensaje_personal(jug_turno_id, msg)
    elif carta == 97: #sal de aquí
            jugador_en_turno_id = juego.posiciones[juego.turno]
            jugador_en_turno    = juego.get_jugador(jugador_en_turno_id)
            jugadores_en_partida  = juego.jugadores_en_partida

            jugadores_no_cuarentena = [jugador for jugador in jugadores_en_partida if not jugador.get_cuartena()]
            lista_jugadores=[]

            for jugador in jugadores_no_cuarentena:
                if jugador.id != jugador_en_turno_id:
                    jugador_dict = {
                        "nombre":jugador.name,
                        "id":jugador.id,
                        "id_avatar":jugador.id_avatar,
                    } 
                    lista_jugadores.append(jugador_dict)

            msg = {"carta_especial":{
                        "tipo_carta":"Sal de aqui",
                        "cartas":[],
                        "jugadores":lista_jugadores,
                    }
                }
            await juego.mensaje_personal(jugador_en_turno_id, msg)

    # revelaciones

    # No podemos ser amigos?
    elif carta in [101, 102]:
        jug_turno = juego.get_jugador_en_turno()
        jug_turno_id = jug_turno.id
        cartas = jug_turno.get_cartas()
        jugadores_en_juego = juego.jugadores_en_partida
        lista_jug = []
        for j in jugadores_en_juego:
            if not is_cuarentena(jug_turno_id,juego):
                jug_nombre = j.name
                jug_id = j.id
                if jug_id != jug_turno_id:
                    jugador = {"nombre": jug_nombre, "id": jug_id}
                    lista_jug.append(jugador)
        msg = {
            "carta_especial": {
		        "tipo_carta":"No podemos ser amigos",
		        "cartas":cartas,
		        "jugadores": lista_jug,
                "request": True,
            }   
        }
        await juego.mensaje_personal(jug_turno_id, msg)
        

    elif carta in [108]:
        pass
    mazo_vacio(juego)
