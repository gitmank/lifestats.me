import app.logging_config  # initialize logging to SQLite
from fastapi import FastAPI
from sqlmodel import SQLModel

from app.db import engine
from app.routes.users import router as users_router
from app.routes.metrics import router as metrics_router

app = FastAPI()

app.include_router(users_router)
app.include_router(metrics_router)