import json

from appredis.redis import get_redis
from diffcheck.lock import ContentLock


class RemoteContentLockStore:
    def __init__(self):
        self._redis_client = get_redis()

    STORE_KEY = "lock:all"

    async def update(self, content_lock: ContentLock) -> None:
        await self._redis_client.json().set(self.STORE_KEY, "$", content_lock)  # type: ignore

    async def get(self) -> ContentLock:
        data = await self._redis_client.json().get(self.STORE_KEY)  # type: ignore
        if data is None:
            return {}

        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                raise TypeError("Stored data is a string but not valid JSON.")

        if not isinstance(data, dict):
            raise TypeError(
                "Stored data is not a dictionary and cannot be coerced to ContentLock."
            )

        content_lock: ContentLock = {}

        for key, value in data.items():
            try:
                file_id = int(key)
            except (ValueError, TypeError):
                raise TypeError(
                    f"ContentLock key '{key}' is not a valid integer (FileId)."
                )

            if not isinstance(value, str):
                raise TypeError(
                    f"ContentLock value for FileId {file_id} is not a string (FileContentHash)."
                )

            content_lock[file_id] = value
        return content_lock
