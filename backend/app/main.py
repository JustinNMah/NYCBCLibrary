from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import init_db
from .routes.auth import router as auth_router
from .routes.checked_out import router as checked_out_router
from .routes.items import router as items_router
from .routes.users import router as users_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="NYCBC Library API", lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "NYCBC Library API"}


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(items_router)
app.include_router(checked_out_router)
