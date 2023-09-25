from fastapi import FastAPI
from models.database import create_db
from models.card_init import create_cards
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

origins = [
    "http://localhost:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.on_event("startup")
def startup_db():
    create_db()
    create_cards()


@app.get("/")
async def root():
    return {"message": "Hello there!"}
