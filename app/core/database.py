from typing import Optional
import asyncpg
from valkey.asyncio import Valkey
from app.core.config import settings


class DatabaseManager:
    db_pool: Optional[asyncpg.Pool] = None
    cache: Optional[Valkey] = None

    @classmethod
    async def connect(cls):
        cls.db_pool = await asyncpg.create_pool(
            dsn=settings.DATABASE_URL,
            min_size=settings.DB_POOL_MIN_SIZE,
            max_size=settings.DB_POOL_MAX_SIZE,
        )
        cls.cache = Valkey.from_url(
            settings.VALKEY_URL,
            decode_responses=False,
        )

    @classmethod
    async def disconnect(cls):
        if cls.db_pool:
            await cls.db_pool.close()
        if cls.cache:
            await cls.cache.aclose()


db_manager = DatabaseManager()
