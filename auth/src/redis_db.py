from redis.asyncio import Redis

from settings import settings

tokens_redis: Redis = Redis(
        host=settings.redis.host,
        port=settings.redis.port,
        db=settings.redis.token_db,
    )


async def get_tokens_redis() -> Redis:
    return tokens_redis