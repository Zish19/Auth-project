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



    def eval(self, script: str, numkeys: int, *keys_and_args):
        import json
        keys = keys_and_args[:numkeys]
        args = keys_and_args[numkeys:]

        # Simple mock for the specific Lua script
        key = keys[0]
        data = self.get(key)
        if not data:
            return 0

        try:
            obj = json.loads(data)
            obj["used"] = True
            self.store[key] = json.dumps(obj)
            return 1
        except Exception:
            return 0
r = DummyRedis()
