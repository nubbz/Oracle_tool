import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SECRET_KEY = os.getenv("SECRET_KEY", "oracle-backup-tool-secret-key-change-in-production-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///C:/Users/zzx/oracle-backup-tool/backend/data.db")

ORACLE_VERSIONS = ["10g", "11g", "12c", "19c", "21c", "23c"]
DEFAULT_ORACLE_VERSION = "19c"
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "")
