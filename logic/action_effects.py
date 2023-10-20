import random
from fastapi import HTTPException
from models.crud import get_name_carta
from models.game import Juego
from utils.action_utils import *


def play_lanzallamas(atacante_in: int, objetivo_in: int, juego: Juego):
    # get indices
    len_posiciones = len(juego.posiciones)
    indice_objetivo = juego.posiciones.index(objetivo_in)
    indice_atacante = juego.posiciones.index(atacante_in)
    indice_posicion_intermedia = get_posicion_intermedia(
        len_posiciones, indice_objetivo, indice_atacante)
    # check vecinos
    validar_posiciones_vecinas(
        indice_atacante,
        indice_objetivo,
        len_posiciones)
    # check obstaculos
    validar_obstaculo(indice_posicion_intermedia, juego)
    for jugador in juego.jugadores_en_partida:
        if jugador.id == objetivo_in:
            # objetivo = jugador
            jugador.set_muerto()
    # juego.jugadores_en_partida.remove(objetivo)
    del juego.posiciones[indice_objetivo]
    del juego.posiciones[indice_objetivo]
    if indice_atacante==max(indice_atacante,indice_objetivo):
        juego.turno = (juego.turno - 2) % len(juego.posiciones)


def play_hacha(atacante_in: int, objetivo_in: int, juego: Juego):
    # get indices
    len_posiciones = len(juego.posiciones)
    indice_objetivo = juego.posiciones.index(objetivo_in)
    indice_atacante = juego.posiciones.index(atacante_in)
    indice_posicion_intermedia = get_posicion_intermedia(
        len_posiciones, indice_objetivo, indice_atacante)
    validar_posiciones_vecinas(
        indice_atacante,
        indice_objetivo,
        len_posiciones)
    validar_puerta(indice_posicion_intermedia, juego)
    juego.posiciones[indice_posicion_intermedia] = 0


def play_sospecha(atacante_in: int, objetivo_in: int, juego: Juego):
    jugador_objetivo = get_jugador(objetivo_in, juego)
    jugador_atacante = get_jugador(atacante_in, juego)
    carta_id = random.choice(jugador_objetivo.cartas)
    if carta_id not in jugador_objetivo.cartas:
        raise HTTPException(
            status_code=400,
            detail="No se pudo obtener una carta del jugador objetivo")
    msg = {"mensaje":jugador_atacante.name+" jugo carta sospecha contra "+jugador_objetivo.name,
           "cartaMostrar": carta_id}
    return msg

def play_vigila_tus_espaldas(juego: Juego):
    juego.sentido = juego.sentido * (-1)


def play_mas_vale_que_corras(atacante_in: int, objetivo_in: int, juego: Juego):
    # validar si esta en cuarentena
    validar_cuarentena(objetivo_in, juego)
    # obtengo el indice de los jugadores
    indice_objetivo = juego.posiciones.index(objetivo_in)
    indice_atacante = juego.posiciones.index(atacante_in)
    # hago el intercambio de posiciones
    juego.posiciones[indice_objetivo] = atacante_in
    juego.posiciones[indice_atacante] = objetivo_in

    if juego.sentido == 1:
            juego.turno = (juego.turno + 2) % len(juego.posiciones)
    elif juego.sentido == -1:
        juego.turno = (juego.turno - 2) % len(juego.posiciones)


async def play_whisky(atacante_in: int, juego: Juego):
    jugador = get_jugador(atacante_in, juego)
    if jugador:
        cartas = jugador.get_cartas()
        msg = {
            "mensaje": jugador.name+ "jugo carta whisky contra si mismo",
            "cartasMostrar": cartas
        }
        await juego.broadcast_global(msg)
    else:
        return {"error": "no se pudieron mostrar cartas"}      
    
def play_cambio_de_lugar(juego:Juego,player_orig:int,player_objective:int):
        
    posiciones = juego.posiciones
    posPorg    = posiciones.index( player_orig )
    posPobj    = posiciones.index( player_objective )

    if(  validar_posiciones_vecinas(posPobj,posPorg,len(posiciones)) ):
        raise HTTPException(
            status_code=400,
            detail="Los jugadores deben ser adyacentes.")

    posiciones[ posPorg ] = player_objective
    posiciones[ posPobj ] = player_orig

    jugadoresEnPartida = juego.jugadores_en_partida    
    indexPOrg = next( (i for i, jugador     in enumerate(jugadoresEnPartida) if jugador.id == player_orig), None )
    indexPobj = next( (i for i, jugador in enumerate(jugadoresEnPartida) if jugador.id == player_objective), None )
    
    pOrg = jugadoresEnPartida[ indexPOrg ]
    pObj = jugadoresEnPartida[ indexPobj ]
    
    pOrg.posicion = posPobj
    pObj.posicion = posPorg    

    if juego.sentido == 1:
            juego.turno = (juego.turno + 2) % len(juego.posiciones)
    elif juego.sentido == -1:
        juego.turno = (juego.turno - 2) % len(juego.posiciones)
