import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from requests import Session
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from . import models, database, routes, schemas
from .database import Base, engine, SessionLocal



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Для разработки можно разрешить все домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = "static"
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
else:
    print(f"Warning: Static files directory '{static_dir}' not found")

app.include_router(routes.router)