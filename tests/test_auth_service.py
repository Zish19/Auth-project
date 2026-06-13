import pytest
from unittest.mock import patch
from fastapi import HTTPException

from app.services.auth_service import verify_login_attempt
from app.crypto.verify import ProofFormatError


@pytest.fixture
def base_args():
    return {
        "username": "testuser",
        "user_public_key": "test_pub_key",
        "challenge_id": "test_challenge",
        "R": "R_value",
        "s": "s_value"
    }


@patch("app.services.auth_service.get_challenge")
def test_verify_login_attempt_challenge_missing(mock_get_challenge, base_args):
    mock_get_challenge.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        verify_login_attempt(**base_args)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid or expired challenge"


@patch("app.services.auth_service.get_challenge")
def test_verify_login_attempt_challenge_used(mock_get_challenge, base_args):
    mock_get_challenge.return_value = {"used": True}

    with pytest.raises(HTTPException) as exc_info:
        verify_login_attempt(**base_args)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Challenge already used"


@patch("app.services.auth_service.get_challenge")
def test_verify_login_attempt_username_mismatch(mock_get_challenge, base_args):
    mock_get_challenge.return_value = {"used": False, "username": "otheruser"}

    with pytest.raises(HTTPException) as exc_info:
        verify_login_attempt(**base_args)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Challenge-user mismatch"


@patch("app.services.auth_service.settings")
@patch("app.services.auth_service.mark_challenge_used")
@patch("app.services.auth_service.create_session")
@patch("app.services.auth_service.get_challenge")
def test_verify_login_attempt_dev_bypass(mock_get_challenge, mock_create_session, mock_mark_used, mock_settings, base_args):
    mock_get_challenge.return_value = {"used": False, "username": "testuser", "challenge": "test_chal_str"}
    mock_settings.AUTH_MODE = "dev_bypass"
    mock_mark_used.return_value = True
    mock_create_session.return_value = "test_session_id"

    result = verify_login_attempt(**base_args)

    assert result == "test_session_id"
    mock_mark_used.assert_called_once_with("test_challenge")
    mock_create_session.assert_called_once_with("testuser")


@patch("app.services.auth_service.settings")
@patch("app.services.auth_service.verify_proof")
@patch("app.services.auth_service.get_challenge")
def test_verify_login_attempt_invalid_proof_format(mock_get_challenge, mock_verify_proof, mock_settings, base_args):
    mock_get_challenge.return_value = {"used": False, "username": "testuser", "challenge": "test_chal_str"}
    mock_settings.AUTH_MODE = "zk"
    mock_verify_proof.side_effect = ProofFormatError("Bad format")

    with pytest.raises(HTTPException) as exc_info:
        verify_login_attempt(**base_args)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Bad format"


@patch("app.services.auth_service.settings")
@patch("app.services.auth_service.verify_proof")
@patch("app.services.auth_service.get_challenge")
def test_verify_login_attempt_unexpected_error(mock_get_challenge, mock_verify_proof, mock_settings, base_args):
    mock_get_challenge.return_value = {"used": False, "username": "testuser", "challenge": "test_chal_str"}
    mock_settings.AUTH_MODE = "zk"
    mock_verify_proof.side_effect = Exception("Unexpected")

    with pytest.raises(HTTPException) as exc_info:
        verify_login_attempt(**base_args)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Unable to verify proof"


@patch("app.services.auth_service.settings")
@patch("app.services.auth_service.verify_proof")
@patch("app.services.auth_service.get_challenge")
def test_verify_login_attempt_invalid_proof(mock_get_challenge, mock_verify_proof, mock_settings, base_args):
    mock_get_challenge.return_value = {"used": False, "username": "testuser", "challenge": "test_chal_str"}
    mock_settings.AUTH_MODE = "zk"
    mock_verify_proof.return_value = False

    with pytest.raises(HTTPException) as exc_info:
        verify_login_attempt(**base_args)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid proof"


@patch("app.services.auth_service.settings")
@patch("app.services.auth_service.verify_proof")
@patch("app.services.auth_service.mark_challenge_used")
@patch("app.services.auth_service.get_challenge")
def test_verify_login_attempt_mark_challenge_failed(mock_get_challenge, mock_mark_used, mock_verify_proof, mock_settings, base_args):
    mock_get_challenge.return_value = {"used": False, "username": "testuser", "challenge": "test_chal_str"}
    mock_settings.AUTH_MODE = "zk"
    mock_verify_proof.return_value = True
    mock_mark_used.return_value = False

    with pytest.raises(HTTPException) as exc_info:
        verify_login_attempt(**base_args)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Unable to update challenge state"


@patch("app.services.auth_service.settings")
@patch("app.services.auth_service.verify_proof")
@patch("app.services.auth_service.create_session")
@patch("app.services.auth_service.mark_challenge_used")
@patch("app.services.auth_service.get_challenge")
def test_verify_login_attempt_session_creation_failed(mock_get_challenge, mock_mark_used, mock_create_session, mock_verify_proof, mock_settings, base_args):
    mock_get_challenge.return_value = {"used": False, "username": "testuser", "challenge": "test_chal_str"}
    mock_settings.AUTH_MODE = "zk"
    mock_verify_proof.return_value = True
    mock_mark_used.return_value = True
    mock_create_session.side_effect = Exception("DB error")

    with pytest.raises(HTTPException) as exc_info:
        verify_login_attempt(**base_args)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Unable to create session"


@patch("app.services.auth_service.settings")
@patch("app.services.auth_service.verify_proof")
@patch("app.services.auth_service.create_session")
@patch("app.services.auth_service.mark_challenge_used")
@patch("app.services.auth_service.get_challenge")
def test_verify_login_attempt_success(mock_get_challenge, mock_mark_used, mock_create_session, mock_verify_proof, mock_settings, base_args):
    mock_get_challenge.return_value = {"used": False, "username": "testuser", "challenge": "test_chal_str"}
    mock_settings.AUTH_MODE = "zk"
    mock_verify_proof.return_value = True
    mock_mark_used.return_value = True
    mock_create_session.return_value = "test_session_id"

    result = verify_login_attempt(**base_args)

    assert result == "test_session_id"
    mock_verify_proof.assert_called_once_with("test_pub_key", "test_chal_str", "R_value", "s_value")
    mock_mark_used.assert_called_once_with("test_challenge")
    mock_create_session.assert_called_once_with("testuser")
