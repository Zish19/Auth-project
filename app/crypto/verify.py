def verify_proof(public_key: str, challenge: str, R: str, s: str) -> bool:
    """
    TODO: Replace with real Schnorr/ECC verification.
    For starter: accept non-empty values only.
    """
    if not (public_key and challenge and R and s):
        return False

    return True