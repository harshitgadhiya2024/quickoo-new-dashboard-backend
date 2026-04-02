from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import get_settings


class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None


mongodb = MongoDB()


async def connect_to_mongo() -> None:
    settings = get_settings()
    mongodb.client = AsyncIOMotorClient(settings.mongodb_uri)
    mongodb.database = mongodb.client[settings.mongodb_db_name]


async def close_mongo_connection() -> None:
    if mongodb.client:
        mongodb.client.close()
        mongodb.client = None
        mongodb.database = None


def get_database() -> AsyncIOMotorDatabase:
    if mongodb.database is None:
        raise RuntimeError("MongoDB is not initialized.")
    return mongodb.database
