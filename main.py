from fastapi import FastAPI
from models.database import create_db
from models.card_init import create_cards
from fastapi.middleware.cors import CORSMiddleware
from endpoints.user import router as user_router
from endpoints.match import router as match_Router
from endpoints.game import router as game_Router
from endpoints.websocket import router as websocket_Router
from os import remove

app = FastAPI()

# Middleware
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Routers
app.include_router(user_router, prefix="/user")
app.include_router(match_Router, prefix="/match")
app.include_router(game_Router, prefix="/game")
app.include_router(websocket_Router, prefix="/ws")


@app.on_event("startup")
def startup_db():
    create_db()
    create_cards()


@app.on_event("shutdown")
def shutdown_event():
    remove("models/database.sqlite")


@app.get("/")
async def root():
    return {"message": "Hello there!"}
