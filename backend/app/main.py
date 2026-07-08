from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .config import DEBUG
from .database import init_db
from .routes.auth import router as auth_router
from .routes.checked_out import router as checked_out_router
from .routes.items import router as items_router
from .routes.users import router as users_router


logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.debug("Starting application lifespan")
    init_db()
    logger.debug("Application startup complete")
    yield


app = FastAPI(title="NYCBC Library API", lifespan=lifespan)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        logger.debug("404 for path %s", request.url.path)
        return JSONResponse(
            status_code=404,
            content={"detail": f"Route not found: {request.url.path}",
                     "exception_detail": exc.detail},
        )
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.get("/")
async def root():
    logger.debug("Root route requested")
    return {"message": "NYCBC Library API"}


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(items_router)
app.include_router(checked_out_router)
