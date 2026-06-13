import pytest
from pydantic import ValidationError
from app.schemas import RegisterRequest

def test_register_request_strip_whitespace():
    # Test that whitespace is stripped from username and public_key
    req = RegisterRequest(
        username="  testuser  ",
        public_key="  testkey  "
    )
    assert req.username == "testuser"
    assert req.public_key == "testkey"

def test_register_request_min_length_after_strip():
    # Test that min_length validation happens AFTER stripping
    with pytest.raises(ValidationError) as exc_info:
        RegisterRequest(username="  ab  ", public_key="k")

    # "ab" is length 2, but min_length is 3. Should fail.
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("username",) for error in errors)
    assert any("String should have at least 3 characters" in error["msg"] for error in errors)

def test_register_request_public_key_min_length_after_strip():
    # Test public_key min_length is 1 after stripping
    with pytest.raises(ValidationError) as exc_info:
        RegisterRequest(username="abc", public_key="   ")

    # "" is length 0, min_length is 1. Should fail.
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("public_key",) for error in errors)
    assert any("String should have at least 1 character" in error["msg"] or "String should have at least 1 characters" in error["msg"] for error in errors)

def test_register_request_valid():
    # Test valid input
    req = RegisterRequest(username="validuser", public_key="validkey")
    assert req.username == "validuser"
    assert req.public_key == "validkey"
