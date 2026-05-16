import os
import base64
import logging

from cryptography.fernet import Fernet

_PREFIX = "enc:"
logger = logging.getLogger(__name__)

_cached_key: bytes | None = None


def _get_key() -> bytes:
    global _cached_key
    if _cached_key is not None:
        return _cached_key

    from app.config import BASE_DIR

    # 1. Try ENCRYPTION_KEY env var (must be a valid Fernet key = 32 url-safe base64 bytes)
    env_key = os.getenv("ENCRYPTION_KEY", "")
    if env_key:
        try:
            key = env_key.encode() if len(env_key) == 44 else base64.urlsafe_b64encode(env_key.encode())
            Fernet(key)  # validate
            _cached_key = base64.urlsafe_b64decode(key)
            return _cached_key
        except Exception:
            logger.warning("ENCRYPTION_KEY is set but invalid, falling back to .secret file")

    # 2. Try .secret file in project root
    secret_path = os.path.join(os.path.dirname(BASE_DIR), ".secret")
    if os.path.exists(secret_path):
        with open(secret_path, "r") as f:
            key_str = f.read().strip()
        if key_str:
            try:
                Fernet(key_str.encode())
                _cached_key = base64.urlsafe_b64decode(key_str.encode())
                return _cached_key
            except Exception:
                logger.warning(".secret file contains invalid key, regenerating")

    # 3. Generate new key and persist
    key = Fernet.generate_key()
    with open(secret_path, "w") as f:
        f.write(key.decode())
    try:
        os.chmod(secret_path, 0o600)
    except OSError:
        pass
    logger.info("Generated new encryption key at %s", secret_path)
    _cached_key = base64.urlsafe_b64decode(key)
    return _cached_key


def encrypt(plaintext: str) -> str:
    f = Fernet(base64.urlsafe_b64encode(_get_key()))
    return _PREFIX + f.encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    if not is_encrypted(ciphertext):
        return ciphertext
    f = Fernet(base64.urlsafe_b64encode(_get_key()))
    return f.decrypt(ciphertext[len(_PREFIX):].encode()).decode()


def is_encrypted(value: str) -> bool:
    return value.startswith(_PREFIX)
