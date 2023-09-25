from fastapi import FastAPI, status, Depends, APIRouter
from fastapi.exceptions import HTTPException
from pony.orm import Database
from models.database_utils import *


router = APIRouter()

@router.post("/user/create", status_code = status.HTTP_201_CREATED)
async def create_user(usuario: str, db: Database = Depends(get_db)):
    try:
        resultado = db_create_user(db, usuario)
        return resultado
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST, 
            detail="Error al crear usuario."
        )