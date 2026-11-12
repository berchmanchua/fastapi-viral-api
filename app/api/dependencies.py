import asyncpg
from valkey.asyncio import Valkey
from fastapi import Depends
from app.core.database import db_manager
from app.services.item_service import ItemService


def get_db_pool() -> asyncpg.Pool:
    assert db_manager.db_pool is not None, "Database pool is not initialized"
    return db_manager.db_pool


def get_cache() -> Valkey:
    assert db_manager.cache is not None, "Valkey cache is not initialized"
    return db_manager.cache


def get_item_service(
    db_pool: asyncpg.Pool = Depends(get_db_pool),
    cache: Valkey = Depends(get_cache),
) -> ItemService:
    return ItemService(db_pool=db_pool, cache=cache)
