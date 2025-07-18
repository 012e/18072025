import json

from appredis.redis import get_redis
from diffcheck.lock import ContentLock


class RemoteContentLockStore:
    def __init__(self):
        self._redis_client = get_redis()

    STORE_KEY = "lock:all"

    async def update(self, content_lock: ContentLock) -> None:
        await self._redis_client.set(self.STORE_KEY, json.dumps(content_lock))

    async def get(self) -> ContentLock:
        return await self._redis_client.get(self.STORE_KEY)
