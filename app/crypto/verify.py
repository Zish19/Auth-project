import base64
import binascii
import hashlib
import logging
import hashlib

from ecdsa import VerifyingKey, SECP256k1, BadSignatureError, MalformedPointError

import ecdsa

logger = logging.getLogger(__name__)


class ProofFormatError(ValueError):
    """Raised when proof inputs are malformed and cannot be parsed safely."""


def _safe_decode_proof_component(value: str) -> bytes:
    normalized = value.strip()
    if not normalized:
        raise ProofFormatError("Proof component cannot be empty")

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
    Safely parse proof inputs and verify using ECDSA over SECP256k1.
    """
    if not (public_key and challenge and R and s):
        return False

    try:
        # 1. Parse components
        pk_bytes = _safe_decode_proof_component(public_key)
        R_bytes = _safe_decode_proof_component(R)
        s_bytes = _safe_decode_proof_component(s)

        curve = ecdsa.SECP256k1
        generator = curve.generator

        # 2. Reconstruct types
        vk = ecdsa.VerifyingKey.from_string(pk_bytes, curve=curve)
        R_point = ecdsa.VerifyingKey.from_string(R_bytes, curve=curve).pubkey.point
        s_int = int.from_bytes(s_bytes, byteorder='big')

        if s_int >= generator.order():
            logger.warning("auth.verify.crypto_error: s value is greater than or equal to curve order")
            return False

        # 3. Hash challenge
        # Secure Fiat-Shamir: h = H(R || pk || challenge)
        hasher = hashlib.sha256()
        hasher.update(R_bytes)
        hasher.update(pk_bytes)
        hasher.update(challenge.encode('utf-8'))
        h = int(hasher.hexdigest(), 16)

        # 4. Schnorr signature verification: s*G == R + h*P
        left = s_int * generator
        right = R_point + (h * vk.pubkey.point)

        is_valid = left == right

        if is_valid:
            logger.debug("auth.verify.proof_verified")
        else:
            logger.debug("auth.verify.proof_invalid")

        return is_valid

    except ProofFormatError:
        raise
    except Exception as e:
        logger.debug(f"auth.verify.schnorr_failed_falling_back: {e}")
        pass

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
    logger.debug("auth.verify.proof_parsed")
    return False
