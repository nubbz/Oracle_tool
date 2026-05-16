from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def migrate_environment_ssh_columns():
    """Add SSH columns to existing environments table if missing."""
    import sqlite3
    db_path = DATABASE_URL.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    new_columns = [
        ("ssh_enabled", "INTEGER DEFAULT 0"),
        ("ssh_host", "VARCHAR(255) DEFAULT ''"),
        ("ssh_port", "INTEGER DEFAULT 22"),
        ("ssh_username", "VARCHAR(100) DEFAULT ''"),
        ("ssh_auth_method", "VARCHAR(10) DEFAULT 'password'"),
        ("ssh_password", "VARCHAR(255) DEFAULT ''"),
        ("ssh_key_path", "VARCHAR(500) DEFAULT ''"),
        ("ssh_key_passphrase", "VARCHAR(255) DEFAULT ''"),
    ]
    for col_name, col_type in new_columns:
        try:
            conn.execute("ALTER TABLE environments ADD COLUMN {} {}".format(col_name, col_type))
        except Exception:
            pass
    conn.commit()
    conn.close()


def migrate_environment_container_columns():
    """Add container_mode and pdb_name columns if missing."""
    import sqlite3
    db_path = DATABASE_URL.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    for col_name, col_type in [("container_mode", "VARCHAR(10) DEFAULT ''"),
                                ("pdb_name", "VARCHAR(100) DEFAULT ''")]:
        try:
            conn.execute("ALTER TABLE environments ADD COLUMN {} {}".format(col_name, col_type))
        except Exception:
            pass
    conn.commit()
    conn.close()


def migrate_encrypt_passwords():
    """Encrypt plain-text SSH passwords already in the database."""
    try:
        from app.services.crypto_service import encrypt, is_encrypted
        import sqlite3
        db_path = DATABASE_URL.replace("sqlite:///", "")
        conn = sqlite3.connect(db_path)
        rows = conn.execute("SELECT id, ssh_password, ssh_key_passphrase FROM environments").fetchall()
        for row_id, pwd, passphrase in rows:
            updates = {}
            if pwd and not is_encrypted(pwd):
                updates["ssh_password"] = encrypt(pwd)
            if passphrase and not is_encrypted(passphrase):
                updates["ssh_key_passphrase"] = encrypt(passphrase)
            if updates:
                set_clause = ", ".join("{} = ?".format(k) for k in updates)
                conn.execute(
                    "UPDATE environments SET {} WHERE id = ?".format(set_clause),
                    list(updates.values()) + [row_id],
                )
        conn.commit()
        conn.close()
    except Exception:
        pass
