from pydantic import BaseModel
from typing import Literal


ALL_STEPS = ["omf", "redolog", "backup", "para", "sqlnet", "glogin"]

# [field_name, flag, default_value]
FLAG_MAP = [
    ("db_name", "-d", "orcl"),
    ("mode", "-m", "rac"),
    ("oracle_user", "-u", "oracle"),
    ("oracle_home", "-o", "/u01/app/oracle/product/19.3.0/db"),
    ("grid_home", "-g", "/u01/app/19.3.0/grid"),
    ("redosize", "-r", 2048),
    ("processes", "-p", 3000),
    ("open_cursors", "-c", 1500),
    ("session_cached_cursors", "-P", 300),
    ("parallel_max_servers", "-R", 64),
    ("undo_retention", "-U", 10800),
    ("db_files", "-F", 5000),
    ("db_memory", "-M", ""),
    ("sga_target", "-S", ""),
    ("pga_target", "-G", ""),
    ("data_asm_group", "-A", "DATA"),
    ("arch_asm_group", "-a", "ARCH"),
    ("backup_dir", "-b", "/backup"),
    ("oradata_dir", "-D", "/oradata"),
]


class OptimizeRequest(BaseModel):
    db_name: str = "orcl"
    mode: Literal["rac", "standalone", "single"] = "rac"
    oracle_user: str = "oracle"
    oracle_home: str = "/u01/app/oracle/product/19.3.0/db"
    grid_home: str = "/u01/app/19.3.0/grid"
    redosize: int = 2048
    processes: int = 3000
    open_cursors: int = 1500
    session_cached_cursors: int = 300
    parallel_max_servers: int = 64
    undo_retention: int = 10800
    db_files: int = 5000
    db_memory: str = ""
    sga_target: str = ""
    pga_target: str = ""
    data_asm_group: str = "DATA"
    arch_asm_group: str = "ARCH"
    oradata_dir: str = "/oradata"
    archive_dir: str = "/oradata/arch"
    backup_dir: str = "/backup"
    steps: list[str] = ALL_STEPS
    restart_after: bool = False


class OptimizeResponse(BaseModel):
    command: str
    params_summary: list[str]
    steps: list[str] = []
