from pydantic import BaseModel
from typing import Optional


class RmanBackupRequest(BaseModel):
    oracle_version: str = "19c"
    # Backup type
    backup_type: str = "full"  # full / incremental / archivelog
    incremental_level: int = 1  # 0 or 1
    # Scope
    scope: str = "database"  # database / tablespace / datafile / controlfile / spfile
    tablespace_name: str = ""
    datafile_path: str = ""
    # Format
    format_tag: str = ""
    format_path: str = "/backup/rman"
    format_pattern: str = "%d_%T_%U"
    # Channels
    channel_count: int = 1
    channel_type: str = "disk"  # disk / sbt
    # Compression
    compression: str = "NONE"  # NONE / LOW / MEDIUM / HIGH / BASIC
    # Encryption
    encryption: str = "NONE"  # NONE / TRANSPARENT / PASSWORD / DUAL
    encryption_algorithm: str = "AES128"  # AES128 / AES192 / AES256
    encryption_password: str = ""
    # Options
    section_size: str = ""  # e.g. "1G"
    skip_offline: bool = False
    skip_readonly: bool = False
    skip_inaccessible: bool = False
    delete_input: bool = False  # for archivelog backup
    # Retention
    retention_policy: str = ""  # e.g. "REDUNDANCY 3", "RECOVERY WINDOW OF 7 DAYS"
    keep_until_time: str = ""
    # Check
    validate: bool = False
    crosscheck: bool = False
    # Tag
    tag: str = ""
    # Connect info (for script generation)
    host: str = "localhost"
    port: int = 1521
    username: str = ""
    password: str = ""
    service_name: str = ""
    sid: str = ""
    connect_type: str = "service"
    oracle_home: str = "/u01/app/oracle/product/19.3.0/dbhome_1"
    # Script options
    include_housekeeping: bool = True


class RmanRestoreRequest(BaseModel):
    oracle_version: str = "19c"
    restore_type: str = "database"  # database / tablespace / controlfile / spfile / archivelog
    tablespace_name: str = ""
    # Point-in-time
    pitr_time: str = ""  # e.g. "2026-05-16 12:00:00"
    pitr_scn: str = ""
    # Until sequence
    until_sequence: str = ""
    until_thread: str = ""
    # From backup
    from_tag: str = ""
    # Options
    preview: bool = False
    validate: bool = False
    # Connect info
    host: str = "localhost"
    port: int = 1521
    username: str = ""
    password: str = ""
    service_name: str = ""
    sid: str = ""
    connect_type: str = "service"
    oracle_home: str = "/u01/app/oracle/product/19.3.0/dbhome_1"


class RmanConfigRequest(BaseModel):
    oracle_version: str = "19c"
    settings: dict = {}
    host: str = "localhost"
    oracle_home: str = "/u01/app/oracle/product/19.3.0/dbhome_1"


class RmanResponse(BaseModel):
    command: str
    script: str
    warnings: list[dict] = []
    recommendations: list[str] = []
    steps: list[str] = []
