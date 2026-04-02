from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.admin import router as admin_router
from app.api.files import router as files_router
from app.api.extra_pickup_type import router as extra_pickup_type_router
from app.api.orders import router as orders_router
from app.api.payments import router as payments_router
from app.api.quotes import router as quotes_router
from app.api.vehicle_class import router as vehicle_class_router
from app.core.config import get_settings
from app.db.indexes import ensure_indexes
from app.db.mongodb import close_mongo_connection, connect_to_mongo


@asynccontextmanager
async def lifespan(_: FastAPI):
    await connect_to_mongo()
    await ensure_indexes()
    yield
    await close_mongo_connection()


settings = get_settings()
app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.include_router(admin_router, prefix="/api/v1")
app.include_router(files_router, prefix="/api/v1")
app.include_router(vehicle_class_router, prefix="/api/v1")
app.include_router(extra_pickup_type_router, prefix="/api/v1")
app.include_router(quotes_router, prefix="/api/v1")
app.include_router(payments_router, prefix="/api/v1")
app.include_router(orders_router, prefix="/api/v1")


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "message": "Quickoo Backend API is running",
        "app_name": settings.app_name,
        "environment": settings.app_env,
        "docs": "/docs",
    }


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}



