import redis.asyncio as aioredis

from app.config import get_settings

redis_client: aioredis.Redis = aioredis.from_url(get_settings().redis_url, decode_responses=True)
