import pytest
import base64
import binascii

from app.crypto.verify import _safe_decode_proof_component, ProofFormatError


def test_empty_string():
    with pytest.raises(ProofFormatError, match="Proof component cannot be empty"):
        _safe_decode_proof_component("")

def test_whitespace_string():
    with pytest.raises(ProofFormatError, match="Proof component cannot be empty"):
        _safe_decode_proof_component("   \t\n")

def test_valid_hex():
    # 'hello' in hex is 68656c6c6f
    assert _safe_decode_proof_component("68656c6c6f") == b"hello"

def test_valid_hex_with_whitespace():
    assert _safe_decode_proof_component("  68656c6c6f  ") == b"hello"

def test_valid_base64url():
    # 'hello' in base64url is aGVsbG8=
    assert _safe_decode_proof_component("aGVsbG8=") == b"hello"

def test_valid_base64url_no_padding():
    assert _safe_decode_proof_component("aGVsbG8") == b"hello"

def test_valid_base64url_with_whitespace():
    assert _safe_decode_proof_component("  aGVsbG8  ") == b"hello"

def test_invalid_format():
    # contains characters invalid for both hex and base64url
    with pytest.raises(ProofFormatError, match="Proof component must be valid hex or base64url"):
        _safe_decode_proof_component("invalid!!__")
