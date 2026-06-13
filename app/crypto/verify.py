import base64
import binascii
import logging
import hashlib

from ecdsa import VerifyingKey, SECP256k1, BadSignatureError, MalformedPointError

logger = logging.getLogger(__name__)


class ProofFormatError(ValueError):
    """Raised when proof inputs are malformed and cannot be parsed safely."""


def _safe_decode_proof_component(value: str) -> bytes:
    normalized = value.strip()
    if not normalized:
        raise ProofFormatError("Proof component cannot be empty")

    # Future Schnorr implementations can replace this with curve-point/scalar parsing.
    try:
        return bytes.fromhex(normalized)
    except ValueError:
        pass

    padded = normalized + "=" * (-len(normalized) % 4)

    try:
        return base64.urlsafe_b64decode(padded.encode("utf-8"))
    except (binascii.Error, ValueError) as exc:
        raise ProofFormatError("Proof component must be valid hex or base64url") from exc


def verify_proof(public_key: str, challenge: str, R: str, s: str) -> bool:
    """
    Safely parse proof inputs and verify using ECDSA over SECP256k1.
    """
    if not (public_key and challenge and R and s):
        return False

    r_bytes = _safe_decode_proof_component(R)
    s_bytes = _safe_decode_proof_component(s)
    vk_bytes = _safe_decode_proof_component(public_key)

    try:
        vk = VerifyingKey.from_string(vk_bytes, curve=SECP256k1)
        sig_bytes = r_bytes + s_bytes
        msg_bytes = challenge.encode("utf-8")
        is_valid = vk.verify(sig_bytes, msg_bytes, hashfunc=hashlib.sha256)
    except (BadSignatureError, MalformedPointError):
        return False
    except Exception as e:
        logger.warning(f"Unexpected error in proof verification: {e}")
        return False

    if is_valid:
        logger.debug("auth.verify.proof_verified")
    return is_valid