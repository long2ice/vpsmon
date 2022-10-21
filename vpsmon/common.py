import redis.asyncio as r

from vpsmon.settings import settings

redis = r.from_url(settings.REDIS_URL, decode_responses=True)  # type:ignore


class RedisKey:
    nonce_cache = "nonce_cache"
