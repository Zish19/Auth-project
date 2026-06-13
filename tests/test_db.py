import pytest
from backend.db import DummyRedis

def test_dummy_redis_init():
    redis = DummyRedis()
    assert redis.store == {}
    assert redis._ttls == {}

def test_dummy_redis_setex_and_get():
    redis = DummyRedis()
    redis.setex("key1", 300, "value1")

    assert redis.get("key1") == "value1"
    assert redis.get("missing_key") is None
