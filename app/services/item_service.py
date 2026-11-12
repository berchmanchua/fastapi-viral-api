from typing import List, Optional
import asyncpg
import orjson
from valkey.asyncio import Valkey
from app.core.config import settings
from app.schemas.item import ItemCreate, ItemUpdate


class ItemService:
    def __init__(self, db_pool: asyncpg.Pool, cache: Valkey):
        self.db_pool = db_pool
        self.cache = cache
        self.ttl = settings.CACHE_TTL_SECONDS

    @staticmethod
    def _cache_key(item_id: int) -> str:
        return f"item:{item_id}"

    async def create_and_cache_item(self, item: ItemCreate) -> dict:
        query = """
            INSERT INTO items (name, description, platform, tags, viral_score)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id, name, description, platform, tags, viral_score
        """
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                query,
                item.name,
                item.description,
                item.platform,
                item.tags,
                item.viral_score,
            )

        new_item = dict(row)
        cache_key = self._cache_key(new_item["id"])
        await self.cache.setex(cache_key, self.ttl, orjson.dumps(new_item))
        return new_item

    async def get_item_by_id(self, item_id: int) -> Optional[dict]:
        cache_key = self._cache_key(item_id)

        cached_bytes = await self.cache.get(cache_key)
        if cached_bytes:
            return orjson.loads(cached_bytes)

        query = """
            SELECT id, name, description, platform, tags, viral_score
            FROM items
            WHERE id = $1 AND deleted_at IS NULL
        """
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(query, item_id)

        if not row:
            return None

        item_data = dict(row)
        await self.cache.setex(cache_key, self.ttl, orjson.dumps(item_data))
        return item_data

    async def list_items(
        self,
        skip: int = 0,
        limit: int = 100,
        platform: Optional[str] = None,
    ) -> List[dict]:
        query = """
            SELECT id, name, description, platform, tags, viral_score
            FROM items
            WHERE deleted_at IS NULL
              AND ($3::varchar IS NULL OR platform = $3)
            ORDER BY id DESC
            OFFSET $1 LIMIT $2
        """
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(query, skip, limit, platform)
        return [dict(r) for r in rows]

    async def update_and_cache_item(self, item_id: int, item: ItemUpdate) -> Optional[dict]:
        query = """
            UPDATE items
            SET name = COALESCE($2, name),
                description = COALESCE($3, description),
                platform = COALESCE($4, platform),
                viral_score = COALESCE($5, viral_score),
                tags = COALESCE($6, tags)
            WHERE id = $1 AND deleted_at IS NULL
            RETURNING id, name, description, platform, tags, viral_score
        """
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                query,
                item_id,
                item.name,
                item.description,
                item.platform,
                item.viral_score,
                item.tags,
            )

        if not row:
            return None

        updated_item = dict(row)
        cache_key = self._cache_key(item_id)
        await self.cache.setex(cache_key, self.ttl, orjson.dumps(updated_item))
        return updated_item

    async def soft_delete_item(self, item_id: int) -> bool:
        query = """
            UPDATE items
            SET deleted_at = NOW()
            WHERE id = $1 AND deleted_at IS NULL
            RETURNING id
        """
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(query, item_id)

        if not row:
            return False

        await self.cache.delete(self._cache_key(item_id))
        return True
