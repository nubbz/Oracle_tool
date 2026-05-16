from pydantic import BaseModel
from typing import Optional


class SqlldrRequest(BaseModel):
    oracle_version: str = "19c"
    # Control file settings
    table_name: str = ""
    data_file: str = ""
    load_method: str = "insert"  # insert / append / replace / truncate
    fields_terminated_by: str = ","
    fields_optionally_enclosed_by: str = '"'
    lines_terminated_by: str = "\n"
    skip_rows: int = 0
    # Column definitions
    columns: str = ""  # comma-separated column definitions
    # Performance
    direct_path: bool = False
    parallel: bool = False
    bindsize: str = ""
    rows: str = ""
    errors: str = ""
    discardmax: str = ""
    # Other
    log_file: str = ""
    bad_file: str = ""
    discard_file: str = ""
    # Connection
    host: str = "localhost"
    port: int = 1521
    username: str = ""
    password: str = ""
    service_name: str = ""
    sid: str = ""
    connect_type: str = "service"


class SqlldrResponse(BaseModel):
    command: str
    control_file: str
    script: str
    warnings: list[dict] = []
    recommendations: list[str] = []
