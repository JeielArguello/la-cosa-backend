from fastapi import status, APIRouter, Form
from fastapi.exceptions import HTTPException
from models.crud import *


router = APIRouter()


@router.post("/create")
async def create_user(user_name: str = Form(), id_avatar: int = Form()):
    try:
        jugador = db_create_user(user_name,id_avatar)
        return jugador
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear usuario."
        )
