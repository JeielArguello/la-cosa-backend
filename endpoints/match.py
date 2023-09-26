from fastapi import HTTPException,Body
from fastapi.routing import APIRouter
from pony.orm import db_session
from fastapi import APIRouter
from models.database import Partida
from models.database_utils import database_utils_iniciar_partida


router = APIRouter()


@db_session
@router.post("/match/start")
async def iniciar_partida(user_id: int = Body(...), match_id: int = Body(...)):
    database_utils_iniciar_partida(match_id,user_id)
    return {"message": "Se inició con éxito la partida."}

