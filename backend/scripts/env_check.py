import asyncio
import sys
from pathlib import Path
import os

# Ensure the script can find the 'core' module
# This adds the parent directory of 'scripts' (i.e., 'backend') to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine
import redis.asyncio as redis
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import UpdateStatus
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def check_database():
    """Checks the database connection."""
    logging.info("Checking database connection...")
    try:
        engine = create_async_engine(settings.database_url, echo=False)
        async with engine.connect() as connection:
            await connection.execute("SELECT 1")
        logging.info("✅ Database connection successful.")
        return True
    except Exception as e:
        logging.error(f"❌ Database connection failed: {e}")
        return False

async def check_redis():
    """Checks the Redis connection."""
    logging.info("Checking Redis connection...")
    try:
        client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        await client.ping()
        logging.info("✅ Redis connection successful.")
        return True
    except Exception as e:
        logging.error(f"❌ Redis connection failed: {e}")
        return False

async def check_qdrant():
    """Checks the Qdrant connection and a basic operation."""
    logging.info("Checking Qdrant connection...")
    try:
        client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)

        # Check health
        health_check_result = client.health_check()
        if not health_check_result:
             raise Exception(f"Qdrant health check failed: {health_check_result}")
        logging.info("Qdrant health check passed.")

        # Perform a basic operation (create and delete a test collection)
        test_collection_name = "env_check_test_collection"

        # Ensure the test collection doesn't exist
        try:
            client.get_collection(collection_name=test_collection_name)
            logging.info(f"Deleting pre-existing test collection: {test_collection_name}")
            client.delete_collection(collection_name=test_collection_name)
        except Exception:
            pass # Collection does not exist, which is good

        client.recreate_collection(
            collection_name=test_collection_name,
            vectors_config=models.VectorParams(size=4, distance=models.Distance.DOT),
        )

        client.upsert(
            collection_name=test_collection_name,
            points=[
                models.PointStruct(
                    id=1,
                    vector=[0.1, 0.2, 0.3, 0.4],
                    payload={"test": "test"},
                )
            ],
            wait=True,
        )

        # Clean up the test collection
        client.delete_collection(collection_name=test_collection_name)

        logging.info("✅ Qdrant connection and basic operations successful.")
        return True
    except Exception as e:
        logging.error(f"❌ Qdrant connection failed: {e}")
        return False

async def main():
    """Runs all environment checks."""
    logging.info("Starting environment checks...")

    # Load .env file if it exists
    from dotenv import load_dotenv
    dotenv_path = Path(__file__).resolve().parent.parent / '.env'
    if dotenv_path.exists():
        load_dotenv(dotenv_path=dotenv_path)
        logging.info(f"Loaded environment variables from {dotenv_path}")
    else:
        logging.warning(f".env file not found at {dotenv_path}. Checks might fail.")

    db_ok = await check_database()
    redis_ok = await check_redis()
    qdrant_ok = await check_qdrant()

    if all([db_ok, redis_ok, qdrant_ok]):
        logging.info("🎉 All environment checks passed successfully!")
        sys.exit(0)
    else:
        logging.error("🔥 Some environment checks failed. Please review the logs.")
        sys.exit(1)

if __name__ == "__main__":
    # This allows running the script with `python -m scripts.env_check` from the `backend` directory
    # or `python backend/scripts/env_check.py` from the repo root.
    if "backend" not in os.getcwd():
        os.chdir("backend")

    # The sys.path manipulation at the top should handle imports.

    asyncio.run(main())
