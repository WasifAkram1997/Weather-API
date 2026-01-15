import os
from redis.asyncio import Redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

redis_client: Redis | None = None

async def initialize_redis() -> Redis:
    global redis_client
    redis_client = Redis.from_url(REDIS_URL, decode_responses=True, socket_timeout=1, socket_connect_timeout=1)
    return redis_client

async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None

async def get_redis() -> Redis:
    global redis_client
    if redis_client is None:
        raise RuntimeError("Redis client is not initialized. Call 'initialize_redis' first.")
    return redis_client