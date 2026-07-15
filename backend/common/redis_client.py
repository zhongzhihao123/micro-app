"""
Redis 客户端 - 缓存 & 会话管理
================================
基于 redis-py 异步客户端，提供：
1. 键值缓存（get/set/get_json/set_json）
2. 滑动窗口限流（check_rate_limit）
3. 分布式锁（acquire_lock/release_lock）
"""
from typing import Optional, Any
import json
import redis.asyncio as aioredis
from .config import get_settings

settings = get_settings()


class RedisClient:
    """异步 Redis 客户端"""

    def __init__(self, redis_url: Optional[str] = None):
        self._url = redis_url or settings.REDIS_URL
        self._pool: Optional[aioredis.ConnectionPool] = None
        self._client: Optional[aioredis.Redis] = None

    async def connect(self):
        if self._client is None:
            self._pool = aioredis.ConnectionPool.from_url(
                self._url,
                max_connections=settings.REDIS_POOL_SIZE,
                decode_responses=True,
            )
            self._client = aioredis.Redis(connection_pool=self._pool)

    async def disconnect(self):
        if self._client:
            await self._client.close()
            self._client = None
            self._pool = None

    @property
    def client(self) -> aioredis.Redis:
        if self._client is None:
            raise RuntimeError("Redis client not connected. Call connect() first.")
        return self._client

    # ---- Cache Operations ----

    async def get(self, key: str) -> Optional[str]:
        return await self.client.get(key)

    async def set(self, key: str, value: str, expire: int = 3600):
        await self.client.set(key, value, ex=expire)

    async def get_json(self, key: str) -> Optional[Any]:
        data = await self.get(key)
        return json.loads(data) if data else None

    async def set_json(self, key: str, value: Any, expire: int = 3600):
        await self.set(key, json.dumps(value, default=str), expire)

    async def delete(self, *keys: str):
        if keys:
            await self.client.delete(*keys)

    async def exists(self, key: str) -> bool:
        return await self.client.exists(key) > 0

    # ---- Rate Limiting ----

    async def check_rate_limit(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """滑动窗口限流，返回是否允许"""
        current = await self.client.incr(key)
        if current == 1:
            await self.client.expire(key, window_seconds)
        return current <= max_requests

    # ---- Distributed Lock ----

    async def acquire_lock(self, lock_name: str, expire: int = 30) -> bool:
        return await self.client.setnx(f"lock:{lock_name}", "1") and await self.client.expire(f"lock:{lock_name}", expire)

    async def release_lock(self, lock_name: str):
        await self.client.delete(f"lock:{lock_name}")


# 全局实例
_redis_client = RedisClient()


async def get_redis() -> RedisClient:
    """FastAPI 依赖注入"""
    if _redis_client._client is None:
        await _redis_client.connect()
    return _redis_client
