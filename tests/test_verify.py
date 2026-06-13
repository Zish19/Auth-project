import pytest
import base64
import binascii

from app.crypto.verify import verify_proof, _safe_decode_proof_component, ProofFormatError
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

def test_verify_proof_valid_hex():
    from ecdsa import SigningKey, SECP256k1
    sk = SigningKey.generate(curve=SECP256k1)
    vk = sk.get_verifying_key()

    public_key = vk.to_string().hex()
    challenge = "dummy_challenge"

    import hashlib
    msg = challenge.encode("utf-8")
    sig = sk.sign(msg, hashfunc=hashlib.sha256)
    R = sig[:32].hex()
    s = sig[32:].hex()

    assert verify_proof(public_key, challenge, R, s) is True

def test_verify_proof_valid_base64url():
    from ecdsa import SigningKey, SECP256k1
    import base64
    sk = SigningKey.generate(curve=SECP256k1)
    vk = sk.get_verifying_key()

    public_key = base64.urlsafe_b64encode(vk.to_string()).decode('utf-8')
    challenge = "dummy_challenge"

    import hashlib
    msg = challenge.encode("utf-8")
    sig = sk.sign(msg, hashfunc=hashlib.sha256)
    R = base64.urlsafe_b64encode(sig[:32]).decode('utf-8')
    s = base64.urlsafe_b64encode(sig[32:]).decode('utf-8')

    assert verify_proof(public_key, challenge, R, s) is True

def test_verify_proof_missing_args():
    # Testing false returns when any argument is empty/missing
    assert verify_proof("", "challenge", "R", "s") is False
    assert verify_proof("pk", "", "R", "s") is False
    assert verify_proof("pk", "challenge", "", "s") is False
    assert verify_proof("pk", "challenge", "R", "") is False
    assert verify_proof(None, "challenge", "R", "s") is False

def test_verify_proof_whitespace_components():
    # Whitespace strings are truthy, so they pass the initial check,
    # but _safe_decode_proof_component should catch and raise ProofFormatError.
    with pytest.raises(ProofFormatError, match="Proof component cannot be empty"):
        verify_proof("pk", "challenge", "   ", "s")

    with pytest.raises(ProofFormatError, match="Proof component cannot be empty"):
        # "s" is invalid empty component, need to provide valid "R" like "deadbeef"
        verify_proof("pk", "challenge", "deadbeef", "\t\n")

def test_verify_proof_invalid_format():
    # Neither hex nor valid base64url
    # "a" translates to "a===" with padding which is invalid base64 (1 data character)
    with pytest.raises(ProofFormatError, match="Proof component must be valid hex or base64url"):
        verify_proof("pk", "challenge", "a", "12345678")

    with pytest.raises(ProofFormatError, match="Proof component must be valid hex or base64url"):
        verify_proof("pk", "challenge", "deadbeef", "a")
