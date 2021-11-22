from fastapi import FastAPI, APIRouter
from sqlmodel import SQLModel
from . import models
from .dependencies import engine
from .routers.api import api

# Init fastapi
app = FastAPI()

# Init routes
app.include_router(api)


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)
