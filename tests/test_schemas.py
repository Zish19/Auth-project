import pytest
from pydantic import ValidationError
from app.schemas import LoginChallengeRequest

def test_login_challenge_request_strip():
    # Test that whitespace is stripped from the beginning and end
    req = LoginChallengeRequest(username="  johndoe  ")
    assert req.username == "johndoe"

def test_login_challenge_request_min_length():
    # Test min length validation (after stripping)
    with pytest.raises(ValidationError):
        LoginChallengeRequest(username=" a ") # length is 1 after strip

def test_login_challenge_request_max_length():
    # Test max length validation
    with pytest.raises(ValidationError):
        LoginChallengeRequest(username="a" * 51)
