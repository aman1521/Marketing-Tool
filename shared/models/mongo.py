from typing import Optional
import os
import logging
import asyncio

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

logger = logging.getLogger(__name__)

_mongo_client: Optional[AsyncIOMotorClient] = None


async def init_mongo(mongo_url: str, document_models: list):
    """Initialize Motor client and Beanie with provided document models."""
    global _mongo_client
    if _mongo_client is None:
        logger.info(f"Initializing MongoDB client: {mongo_url}")
        _mongo_client = AsyncIOMotorClient(mongo_url)

    # Initialize Beanie with the Motor client database and document models
    db_name = mongo_url.rsplit('/', 1)[-1] or os.getenv("MONGO_DB", "aios_database")
    await init_beanie(database=_mongo_client[db_name], document_models=document_models)
    logger.info("Beanie initialized with document models")


def get_mongo_client() -> Optional[AsyncIOMotorClient]:
    return _mongo_client


def close_mongo():
    global _mongo_client
    if _mongo_client:
        logger.info("Closing MongoDB client connection")
        _mongo_client.close()
        _mongo_client = None
