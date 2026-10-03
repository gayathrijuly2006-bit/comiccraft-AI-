from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import APP_NAME, DEBUG, STATIC_DIR
from app.routes import router

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.getLogger(__name__).info("%s started", APP_NAME)
    yield
    logging.getLogger(__name__).info("%s stopped", APP_NAME)


app = FastAPI(
    title=APP_NAME,
    version="1.0.0",
    description="AI comic generator built with FastAPI, Jinja2, Gemini, Hugging Face and FPDF.",
    debug=DEBUG,
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.include_router(router)
