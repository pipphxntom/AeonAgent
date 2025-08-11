from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData
import logging
from typing import Optional

from .config import settings

# Database metadata
metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }
)

# SQLAlchemy base
Base = declarative_base(metadata=metadata)

engine = None  # type: ignore
AsyncSessionLocal: Optional[async_sessionmaker[AsyncSession]] = None


async def init_db():
    """Initialize database."""
    try:
        global engine, AsyncSessionLocal

        if engine is None:
            db_url = settings.database_url
            engine = create_async_engine(
                db_url,
                echo=settings.ENVIRONMENT == "development",
                future=True,
                pool_pre_ping=True,
                pool_recycle=300,
            )
            AsyncSessionLocal = async_sessionmaker(
                engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,
                autocommit=False,
            )

            # Import models lazily to avoid circular imports (models import Base from this module)
            import models  # noqa: F401

            if settings.ENVIRONMENT == "development":
                async with engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
        
        logging.info("Database initialized successfully")
    except Exception as e:
        logging.error(f"Failed to initialize database: {e}")
        raise


async def get_db() -> AsyncSession:
    """Get database session."""
    if AsyncSessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() during startup before using get_db().")
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_engine():
    if engine is None:
        raise RuntimeError("Engine not initialized. Call init_db() first.")
    return engine
