from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from . import models, database, routes

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.include_router(routes.router)
app.mount("/static", StaticFiles(directory="static"), name="static")