# app/db.py

class DummyRedis:
    def __init__(self):
        self.store: dict = {}
        self._ttls: dict = {}

    def setex(self, key: str, seconds: int, value: str) -> None:
        self.store[key] = value
        self._ttls[key] = seconds

    def get(self, key: str) -> str | None:
        return self.store.get(key)

    def ttl(self, key: str) -> int:
        return self._ttls.get(key, 60)

    def delete(self, key: str) -> None:
        self.store.pop(key, None)
        self._ttls.pop(key, None)


r = DummyRedis()