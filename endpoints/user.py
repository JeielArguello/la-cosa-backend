from fastapi import status, APIRouter, Form
from fastapi.exceptions import HTTPException
from models.crud import *


router = APIRouter()


@router.post("/create")
async def create_user(usuario: str = Form()):
    try:
        jugador = db_create_user(usuario)
        return jugador
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear usuario."
        )
