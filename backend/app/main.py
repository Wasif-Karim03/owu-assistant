import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routers import chat, admin
from app.routers.health import router as health_router
from app.ingestion.schedule import start_refresh_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    start_refresh_scheduler()
    yield


app = FastAPI(
    title="OWU Campus Assistant API",
    version="0.1.0",
    lifespan=lifespan,
)

_origins = [settings.FRONTEND_URL]
if settings.ENVIRONMENT == "production":
    _origins.append("https://*.vercel.app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"status": "ok", "service": "OWU Campus Assistant"}


app.include_router(chat.router)
app.include_router(admin.router)
app.include_router(health_router)
