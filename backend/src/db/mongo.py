"""MongoDB connection and health check utilities."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure

from ..utils.logger import get_logger

logger = get_logger("backend.db.mongo", "/app/logs/backend.api.log")

# Global client instance
mongo_client: AsyncIOMotorClient | None = None
db: AsyncIOMotorDatabase | None = None


async def connect_to_mongo(mongodb_url: str) -> None:
    """
    Connect to MongoDB and initialize database.

    Args:
        mongodb_url: MongoDB connection string
    """
    global mongo_client, db

    try:
        mongo_client = AsyncIOMotorClient(mongodb_url)
        # Test connection
        await mongo_client.admin.command("ping")

        # Get database from URL or use default
        db_name = mongodb_url.split("/")[-1] if "/" in mongodb_url else "intelligence"
        db = mongo_client[db_name]

        logger.info("Successfully connected to MongoDB", extra={"database": db_name})
    except ConnectionFailure as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_mongo_connection() -> None:
    """Close MongoDB connection."""
    global mongo_client

    if mongo_client:
        mongo_client.close()
        logger.info("MongoDB connection closed")


async def check_mongo_health() -> bool:
    """
    Check MongoDB connection health.

    Returns:
        True if MongoDB is healthy, False otherwise
    """
    global mongo_client

    if not mongo_client:
        return False

    try:
        await mongo_client.admin.command("ping")
        return True
    except Exception as e:
        logger.error(f"MongoDB health check failed: {e}")
        return False


def get_database() -> AsyncIOMotorDatabase:
    """
    Get the current database instance.

    Returns:
        AsyncIOMotorDatabase instance

    Raises:
        RuntimeError: If database is not initialized
    """
    if db is None:
        raise RuntimeError("Database not initialized. Call connect_to_mongo() first.")
    return db
