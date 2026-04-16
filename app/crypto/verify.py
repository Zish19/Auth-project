import base64
import binascii
import logging

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
    Safely parse proof inputs before real cryptographic verification is added.

    TODO: Replace the placeholder return path with real Schnorr/ECC verification
    after parsing `public_key`, `challenge`, `R`, and `s` into the expected types.
    """
    if not (public_key and challenge and R and s):
        return False

    _safe_decode_proof_component(R)
    _safe_decode_proof_component(s)

    logger.debug("auth.verify.proof_parsed")
    return True