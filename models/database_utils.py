from fastapi import HTTPException,Body
from pony.orm import db_session
from models.database import Partida


@db_session
def database_utils_iniciar_partida(match_id:int,user_id:int):
    with db_session:
        try: partida = Partida.get(id=match_id)
        except: raise HTTPException(status_code=400, detail="Error al acceder a la base de datos.")
        
        if partida is None:
            raise HTTPException(status_code=400, detail="El match_id no es válido")

        if partida.id_jugador_creador != user_id:
            raise HTTPException(status_code=400, detail="El user_id no corresponde al creador de la ")
        
        if partida.iniciado == True:
            raise HTTPException(status_code=400, detail="La partida ya esta inicializada.")
        
        try: partida.iniciado = True
        except:raise HTTPException(status_code=400, detail="No se le pudo inicializar la ")
       
