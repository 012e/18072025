from diffcheck.lock import ContentLock

data: ContentLock = {}


class LocalContentLockStore:
    def update(self, content_lock: ContentLock) -> None:
        data = content_lock

    def get(self):
        return data
