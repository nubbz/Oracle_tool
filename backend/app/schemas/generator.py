from pydantic import BaseModel
from typing import Literal


class ConnectionParams(BaseModel):
    username: str = ""
    password: str = ""
    auth_method: Literal["password", "wallet", "os"] = "password"
    connect_type: Literal["service", "sid"] = "service"
    service_name: str = ""
    sid: str = ""
    host: str = "localhost"
    port: int = 1521
    # SSH Tunnel
    ssh_enabled: bool = False
    ssh_host: str = ""
    ssh_port: int = 22
    ssh_username: str = ""
    ssh_auth_method: Literal["password", "key"] = "password"
    ssh_password: str = ""
    ssh_key_path: str = ""
    ssh_key_passphrase: str = ""
    # Container Database
    container_mode: str = ""
    pdb_name: str = ""


class ExpdpParams(BaseModel):
    directory: str = ""
    dumpfile: str = ""
    schemas: list[str] = []
    tables: list[str] = []
    tablespaces: list[str] = []
    query: str = ""
    content: Literal["ALL", "METADATA_ONLY", "DATA_ONLY"] = "ALL"
    exclude: list[str] = []
    include: list[str] = []
    filesize: str = ""
    reuse_dumpfiles: bool = False
    version: str = ""
    flashback_scn: str = ""
    flashback_time: str = ""
    encryption: str = ""
    encryption_password: str = ""
    encryption_mode: str = ""
    encryption_columns_only: list[str] = []
    transportable: bool = False
    transport_full_check: bool = False
    parallel: int = 1
    logfile: str = ""
    compression: Literal["ALL", "DATA_ONLY", "METADATA_ONLY", "NONE"] = "NONE"
    job_name: str = ""
    estimate: Literal["BLOCKS", "STATISTICS", ""] = ""


class ExpParams(BaseModel):
    file: str = ""
    owner: list[str] = []
    tables: list[str] = []
    query: str = ""
    direct: bool = False
    compress: bool = False
    consistent: bool = False
    statistics: str = "ESTIMATE"
    buffer: str = ""
    rows: bool = True
    indexes: bool = True
    constraints: bool = True
    grants: bool = True
    triggers: bool = True
    feedback: int = 0
    file_size: str = ""
    resumable: bool = False
    resumable_name: str = ""
    resumable_timeout: int = 0
    recordlength: int = 0
    object_consistent: bool = False
    parallel: int = 1
    logfile: str = ""
    compression: bool = False


class ImpdpParams(BaseModel):
    directory: str = ""
    dumpfile: str = ""
    schemas: list[str] = []
    tables: list[str] = []
    remap_schema: str = ""
    remap_tablespace: str = ""
    remap_datafile: str = ""
    remap_table: str = ""
    table_exists_action: Literal["SKIP", "APPEND", "TRUNCATE", "REPLACE"] = ""
    content: Literal["ALL", "METADATA_ONLY", "DATA_ONLY"] = "ALL"
    exclude: list[str] = []
    include: list[str] = []
    transform: str = ""
    sqlfile: str = ""
    partition_options: str = ""
    data_options: str = ""
    disable_archive_logging: bool = False
    encryption_password: str = ""
    version: str = ""
    flashback_scn: str = ""
    flashback_time: str = ""
    network_link: str = ""
    reuse_datafiles: bool = False
    reuse_dumpfiles: bool = False
    parallel: int = 1
    logfile: str = ""
    compression: Literal["ALL", "DATA_ONLY", "METADATA_ONLY", "NONE"] = "NONE"
    job_name: str = ""
    logtime: Literal["ALL", "HEADER", "LOGFILE", "STATUS", ""] = ""
    metrics: bool = False


class ImpParams(BaseModel):
    file: str = ""
    fromuser: list[str] = []
    touser: list[str] = []
    tables: list[str] = []
    commit: bool = False
    ignore: bool = False
    buffer: str = ""
    statistics: str = "RECALCULATE"
    indexes: bool = True
    constraints: bool = True
    grants: bool = True
    triggers: bool = True
    rows: bool = True
    feedback: int = 0
    recordlength: int = 0
    resumable: bool = False
    resumable_name: str = ""
    resumable_timeout: int = 0
    show: bool = False
    destroy: bool = False
    compile: bool = False
    indexfile: str = ""
    skip_unusable_indexes: bool = False
    streamsize: str = ""
    toid_novalidate: list[str] = []
    filesize: str = ""
    parallel: int = 1
    logfile: str = ""
    compression: bool = False


class GenerateRequest(BaseModel):
    tool: Literal["expdp", "exp", "impdp", "imp"]
    oracle_version: Literal["10g", "11g", "12c", "19c", "21c", "23c"] = "19c"
    connection: ConnectionParams
    params: dict


class ValidationWarning(BaseModel):
    level: Literal["error", "warning", "info"]
    field: str
    message: str
    suggestion: str | None = None


class GenerateResponse(BaseModel):
    command: str
    parfile: str
    script: str
    warnings: list[ValidationWarning]
    recommendations: list[str]
    directory_ddl: str = ""
    steps: list[str] = []
