from functools import lru_cache

import redis.asyncio as redis

from config.config import load_config


@lru_cache(maxsize=1)
def get_redis():
    """Returns a Redis client instance."""
    config = load_config()

    return redis.Redis(
        host=config.redis_host,
        port=config.redis_port,
        password=config.redis_password,
        decode_responses=True,  # Ensure strings are returned as str, not bytes
    )
