from fastapi import FastAPI
from src.database import db_open, db_close
from contextlib import asynccontextmanager
from src.routes.cards import cards_router
from src.routes.characters import characters_router
from src.routes.trivias import trivias_router
from src.routes.items import items_router
from dotenv import load_dotenv
import uvicorn
import os


load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    db_open()
    yield
    db_close()


app = FastAPI(lifespan=lifespan, version="1.0.0")


app.include_router(cards_router, prefix="/api", tags=["cards"])
app.include_router(characters_router, prefix="/api", tags=["characters"])
app.include_router(trivias_router, prefix="/api", tags=["trivias"])
app.include_router(items_router, prefix="/api", tags=["items"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST"),
        port=int(os.getenv("API_HOST_PORT")),
        reload=True
    )