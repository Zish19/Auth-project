# app/db.py

class DummyRedis:
    def __init__(self):
        self.store = {}
        self.ttl = {}

    def setex(self, key, seconds, value):
        self.store[key] = value

    def get(self, key):
        return self.store.get(key)

    def ttl(self, key):
        return 60

    def delete(self, key):
        if key in self.store:
            del self.store[key]


r = DummyRedis()