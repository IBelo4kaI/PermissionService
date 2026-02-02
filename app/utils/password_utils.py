import hashlib
import os


def hash_password(password: str) -> str:
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return salt.hex() + key.hex()


def verify_password(stored_password: str, provided_password: str) -> bool:
    salt = bytes.fromhex(stored_password[:64])
    stored_key = stored_password[64:]

    provided_key = hashlib.pbkdf2_hmac(
        "sha256", provided_password.encode("utf-8"), salt, 100000
    ).hex()

    # Сравниваем ключи
    return stored_key == provided_key
