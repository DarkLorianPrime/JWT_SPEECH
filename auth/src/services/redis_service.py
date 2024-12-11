import json
from functools import lru_cache
from typing import Annotated, Any
from uuid import UUID

from fastapi import Depends
from redis.asyncio.client import Redis

from redis_db import get_tokens_redis
from jwt_auth.abstract.classes import TokenControllerAbstract


class TokensRedisController(TokenControllerAbstract):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get_from_cache(
        self, detail_uuid: UUID | str
    ) -> dict[str, Any] | Any | None:
        data = await self.redis.get(str(detail_uuid))
        if data:
            return json.loads(data)

        return None

    async def put_to_cache(self, put_object: dict, ttl: int):
        put_object_or = json.dumps(put_object)
        await self.redis.set(put_object["id"], put_object_or, abs(int(ttl)))


@lru_cache
def get_tokens_controller(redis_tokens: Annotated[Redis, Depends(get_tokens_redis)]):
    return TokensRedisController(redis_tokens)
