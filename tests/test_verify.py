import pytest
from app.crypto.verify import verify_proof, ProofFormatError

def test_verify_proof_valid_hex():
    # Valid hex values for R and s
    public_key = "dummy_pk"
    challenge = "dummy_challenge"
    R = "deadbeef"
    s = "12345678"
    assert verify_proof(public_key, challenge, R, s) is True

def test_verify_proof_valid_base64url():
    # Valid base64url values (could have padding or not)
    public_key = "dummy_pk"
    challenge = "dummy_challenge"
    R = "YmFzZTY0"  # base64 for "base64"
    s = "dGVzdA"  # base64 for "test"
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
