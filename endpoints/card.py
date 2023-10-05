from pony.orm import db_session, select
from fastapi import FastAPI, status


app = FastAPI()

@app.get("/")
async def root(): return {"message": "Hello World"}
