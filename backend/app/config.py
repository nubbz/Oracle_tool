import os
import secrets
import logging

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))

_DEFAULT_SECRET = "oracle-backup-tool-secret-key-change-in-production-2026"


def _resolve_secret_key() -> str:
    env_key = os.getenv("SECRET_KEY", "")
    if env_key:
        return env_key

    secret_path = os.path.join(PROJECT_ROOT, ".jwt_secret")
    if os.path.exists(secret_path):
        with open(secret_path, "r") as f:
            key = f.read().strip()
        if key:
            return key

    key = secrets.token_urlsafe(48)
    with open(secret_path, "w") as f:
        f.write(key)
    try:
        os.chmod(secret_path, 0o600)
    except OSError:
        pass
    logger.warning("JWT secret auto-generated and saved to %s", secret_path)
    return key


SECRET_KEY = os.getenv("SECRET_KEY", "")
if SECRET_KEY == _DEFAULT_SECRET:
    logger.warning("Using default JWT SECRET_KEY — set SECRET_KEY env var for production!")
    SECRET_KEY = _resolve_secret_key()
elif SECRET_KEY:
    pass
else:
    SECRET_KEY = _resolve_secret_key()

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{PROJECT_ROOT}/data.db".replace("\\", "/"))

ORACLE_VERSIONS = ["10g", "11g", "12c", "19c", "21c", "23c"]
DEFAULT_ORACLE_VERSION = "19c"
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "")
