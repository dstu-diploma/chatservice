from fastapi.middleware.cors import CORSMiddleware
from app.dependencies import get_event_consumer
from contextlib import asynccontextmanager
from app.events import register_events
from app.routers import main_router
import app.events.registered as _
from .config import Settings
from fastapi import FastAPI
from app.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    consumer = get_event_consumer()
    await consumer.connect()
    task = await register_events(consumer)

    yield

    task.cancel()
    await task


app = FastAPI(
    title="DSTU Diploma | ChatService",
    docs_url="/swagger",
    root_path=Settings.ROOT_PATH,
    lifespan=lifespan,
)

init_db(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(main_router)
