import os
import base64

_PREFIX = "enc:"


def _get_key() -> bytes:
    from cryptography.fernet import Fernet
    from app.config import BASE_DIR, ENCRYPTION_KEY

    key_str = ENCRYPTION_KEY
    if key_str:
        return base64.urlsafe_b64decode(key_str.encode() if len(key_str) > 32 else Fernet.generate_key())

    secret_path = os.path.join(os.path.dirname(BASE_DIR), ".secret")
    if os.path.exists(secret_path):
        with open(secret_path, "r") as f:
            key_str = f.read().strip()
        if key_str:
            return base64.urlsafe_b64decode(key_str.encode())

    key = Fernet.generate_key()
    with open(secret_path, "w") as f:
        f.write(key.decode())
    os.chmod(secret_path, 0o600)
    return base64.urlsafe_b64decode(key)


def encrypt(plaintext: str) -> str:
    from cryptography.fernet import Fernet
    f = Fernet(base64.urlsafe_b64encode(_get_key()))
    return _PREFIX + f.encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    from cryptography.fernet import Fernet
    if not is_encrypted(ciphertext):
        return ciphertext
    f = Fernet(base64.urlsafe_b64encode(_get_key()))
    return f.decrypt(ciphertext[len(_PREFIX):].encode()).decode()


def is_encrypted(value: str) -> bool:
    return value.startswith(_PREFIX)
