import hashlib
import secrets


def generate_token() -> str:
    return secrets.token_hex(32)


def create_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
