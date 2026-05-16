import re
import shlex
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional


class BaseGenerator(ABC):
    """命令生成器基类，提供连接串构建和参数格式化工具方法"""

    TOOL_NAME: str = ""

    def __init__(self, connection: dict, params: dict, oracle_version: str = "19c"):
        self.connection = connection
        self.params = params
        self.oracle_version = oracle_version
        self._parts: list[str] = []
        self._parfile_lines: list[str] = []
        self._built = False
        self._added_params: list[tuple[str, str]] = []

    @staticmethod
    def _safe_sql_id(name: str) -> str:
        """Validate a SQL identifier (table/schema/directory name)."""
        if not re.match(r'^[A-Za-z_][A-Za-z0-9_$#]*$', name):
            raise ValueError(f"Invalid SQL identifier: {name}")
        return name

    @staticmethod
    def _sq(value) -> str:
        """Shell-quote a value for safe embedding in scripts."""
        return shlex.quote(str(value))

    def build_connect_string(self) -> str:
        auth_method = self.connection.get("auth_method", "password")
        connect_type = self.connection.get("connect_type", "service")
        username = self.connection.get("username", "")
        password = self.connection.get("password", "")
        host = self.connection.get("host", "localhost")
        port = self.connection.get("port", 1521)

        if auth_method == "wallet":
            return f"{username}@{host}:{port}/{self._get_identifier(connect_type)}"
        elif auth_method == "os":
            return "/ as sysdba"
        else:
            ident = self._get_identifier(connect_type)
            return f'{username}/"{password}"@{host}:{port}/{ident}'

    def _get_identifier(self, connect_type: str) -> str:
        if connect_type == "sid":
            return self.connection.get("sid", "orcl")
        return self.connection.get("service_name", "orcl")

    def _add_param(self, key: str, value) -> bool:
        if value is None or value == "" or value == 0 or value is False:
            return False
        if isinstance(value, bool):
            if value:
                self._parts.append(f"{key}={self._format_value(value)}")
                self._parfile_lines.append(f"{key}={self._format_value(value)}")
                return True
            return False
        if isinstance(value, list) and len(value) == 0:
            return False
        self._parts.append(f"{key}={self._format_value(value)}")
        self._parfile_lines.append(f"{key}={self._format_value(value)}")
        self._added_params.append((key, self._format_value(value)))
        return True

    def _format_value(self, value) -> str:
        if isinstance(value, bool):
            return "Y" if value else "N"
        if isinstance(value, list):
            return ",".join(str(v) for v in value)
        return str(value)

    def generate_command(self) -> str:
        self._do_build()
        connect_str = self.build_connect_string()
        if self.connection.get("auth_method") == "os":
            connect_str = f"'{connect_str}'"
        if self._parts:
            return f"{self.TOOL_NAME} {connect_str} \\\n  " + " \\\n  ".join(self._parts)
        return f"{self.TOOL_NAME} {connect_str}"

    def generate_parfile(self) -> str:
        self._do_build()
        connect_str = self.build_connect_string()
        lines = [f"# {self.TOOL_NAME} Parameter File", f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ""]
        if not connect_str.startswith("/"):
            lines.append(f"# Connection: {connect_str}")
        lines.extend(self._parfile_lines)
        return "\n".join(lines)

    def _do_build(self):
        if not self._built:
            self._build_params()
            self._built = True

    def generate_steps(self) -> list[str]:
        """Generate Chinese step descriptions explaining what the command does."""
        self._do_build()
        return self._build_steps()

    def _build_steps(self) -> list[str]:
        """Override in subclasses to provide tool-specific step descriptions."""
        return []

    def _step_connect(self) -> str:
        auth = self.connection.get("auth_method", "password")
        host = self.connection.get("host", "localhost")
        port = self.connection.get("port", 1521)
        connect_type = self.connection.get("connect_type", "service")
        ident = self._get_identifier(connect_type)
        username = self.connection.get("username", "")

        if auth == "os":
            return "以 OS 认证方式连接数据库 (sysdba)"
        if auth == "wallet":
            return f"通过 Oracle Wallet 认证连接 {username}@{host}:{port}/{ident}"
        return f"连接到数据库 {username}@{host}:{port}/{ident}"

    def generate_script(self, script_type: str = "sh") -> str:
        command = self.generate_command()
        if script_type == "bat":
            return self._generate_bat_script(command)
        return self._generate_sh_script(command)

    def _generate_sh_script(self, command: str) -> str:
        connect_type = self.connection.get("connect_type", "service")
        ident_label = "SID" if connect_type == "sid" else "SERVICE_NAME"
        ident_value = self._get_identifier(connect_type)
        host = self.connection.get("host", "localhost")
        port = self.connection.get("port", 1521)
        username = self.connection.get("username", "")
        tool = self.TOOL_NAME.upper()

        lines = [
            "#!/bin/bash",
            "# ============================================================",
            "# Oracle {} Script".format(tool),
            "# Generated: {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "# Tool: Oracle Backup Command Generator v1.0",
            "# ============================================================",
            "",
            "# --- Environment ---",
            "ORACLE_HOME=${ORACLE_HOME:-/u01/app/oracle/product/19.3.0/dbhome_1}",
            "export ORACLE_HOME",
            "export PATH=$ORACLE_HOME/bin:$PATH",
            "export LD_LIBRARY_PATH=$ORACLE_HOME/lib:$LD_LIBRARY_PATH",
            "",
            "# --- Connection ---",
            "DB_HOST={}".format(self._sq(host)),
            "DB_PORT={}".format(self._sq(port)),
            "DB_USER={}".format(self._sq(username)),
            "DB_{}={}".format(ident_label, self._sq(ident_value)),
            'DB_PASS="***"  # 请替换为实际密码，建议使用 Oracle Wallet',
            "CONTAINER_MODE={}".format(self._sq(self.connection.get("container_mode", ""))),
            "PDB_NAME={}".format(self._sq(self.connection.get("pdb_name", ""))),
            "",
            "# --- Timestamp ---",
            "TIMESTAMP=$(date +%Y%m%d_%H%M%S)",
            "",
            "# --- Pre-check ---",
            'echo "[$(date +\\"%Y-%m-%d %H:%M:%S\\")] Starting {}..."'.format(tool),
            "",
            "# 检查 Oracle 实例状态",
            "PMON_COUNT=$(ps -ef | grep -c '[o]ra_pmon_')",
            "if [ $PMON_COUNT -eq 0 ]; then",
            '    echo "[ERROR] Oracle instance process (pmon) not found!"',
            "    exit 1",
            "fi",
        ]

        # SSH Tunnel
        ssh_enabled = self.connection.get("ssh_enabled")
        if ssh_enabled:
            ssh_host = self.connection.get("ssh_host", "")
            ssh_port = self.connection.get("ssh_port", 22)
            ssh_user = self.connection.get("ssh_username", "")
            ssh_auth = self.connection.get("ssh_auth_method", "password")
            ssh_pwd = self.connection.get("ssh_password", "")
            ssh_key = self.connection.get("ssh_key_path", "")

            lines.extend([
                "",
                "# --- SSH Tunnel ---",
                "SSH_TUNNEL_HOST={}".format(self._sq(ssh_host)),
                "SSH_TUNNEL_PORT={}".format(self._sq(ssh_port)),
                "SSH_TUNNEL_USER={}".format(self._sq(ssh_user)),
                "SSH_REMOTE_HOST={}".format(self._sq(host)),
                "SSH_REMOTE_PORT={}".format(self._sq(port)),
                "SSH_LOCAL_PORT=15210",
                "",
                "# Auto-select available local port",
                "while ss -tln 2>/dev/null | grep -q \":${SSH_LOCAL_PORT} \"; do",
                "    SSH_LOCAL_PORT=$((SSH_LOCAL_PORT + 1))",
                "done",
            ])

            if ssh_auth == "key":
                lines.extend([
                    "",
                    "ssh -fNL $SSH_LOCAL_PORT:$SSH_REMOTE_HOST:$SSH_REMOTE_PORT \\",
                    "    -i {} \\".format(self._sq(ssh_key)),
                    "    -p $SSH_TUNNEL_PORT \\",
                    "    -o StrictHostKeyChecking=no \\",
                    "    $SSH_TUNNEL_USER@$SSH_TUNNEL_HOST",
                ])
            else:
                lines.extend([
                    "",
                    "# Check sshpass",
                    "if ! command -v sshpass >/dev/null 2>&1; then",
                    '    echo "[ERROR] sshpass is required. Install: apt-get install sshpass"',
                    "    exit 1",
                    "fi",
                    "sshpass -p {} ssh -fNL $SSH_LOCAL_PORT:$SSH_REMOTE_HOST:$SSH_REMOTE_PORT \\".format(self._sq(ssh_pwd)),
                    "    -p $SSH_TUNNEL_PORT \\",
                    "    -o StrictHostKeyChecking=no \\",
                    "    $SSH_TUNNEL_USER@$SSH_TUNNEL_HOST",
                ])

            lines.extend([
                "",
                "sleep 1",
                'SSH_PID=$(ss -tlnp 2>/dev/null | grep ":${SSH_LOCAL_PORT}" | grep -oP "pid=\\K[0-9]+" | head -1)',
                'if [ -z "$SSH_PID" ]; then',
                '    echo "[ERROR] Failed to establish SSH tunnel!"',
                "    exit 1",
                "fi",
                'echo "[INFO] SSH tunnel established (PID: $SSH_PID, local port: $SSH_LOCAL_PORT)"',
                "",
                "# Cleanup tunnel on exit",
                """trap 'if [ -n "$SSH_PID" ]; then kill $SSH_PID 2>/dev/null; echo "[INFO] SSH tunnel closed"; fi' EXIT""",
                "",
                "# Override connection to use tunnel",
                'DB_HOST="127.0.0.1"',
                'DB_PORT="$SSH_LOCAL_PORT"',
            ])

        # expdp/impdp 磁盘空间检查
        directory = self.params.get("directory", "")
        if directory and self.TOOL_NAME in ("expdp", "impdp"):
            lines.extend([
                "",
                "# 检查 Directory 磁盘空间（{}）".format(directory),
                'echo "[INFO] Please verify disk space for Directory: {}"'.format(directory),
            ])

        lines.extend([
            "",
            "# --- Execute ---",
        ])

        if self.connection.get("auth_method") == "os":
            lines.append("{0} '\"'/ as sysdba'\"' \\".format(self.TOOL_NAME))
        else:
            ident_var = "DB_{}".format(ident_label)
            lines.append(self.TOOL_NAME + ' "${DB_USER}/${DB_PASS}@${DB_HOST}:${DB_PORT}/${' + ident_var + '}" \\')

        for i, p in enumerate(self._parts):
            if i < len(self._parts) - 1:
                lines.append("  {} \\".format(p))
            else:
                lines.append("  {}".format(p))

        lines.extend([
            "",
            "# --- Result Check ---",
            "RC=$?",
            "if [ $RC -eq 0 ]; then",
            '    echo "[$(date +\\"%Y-%m-%d %H:%M:%S\\")] {} completed successfully."'.format(tool),
            "    # 检查日志中的 ORA- 错误",
            '    if [ -n "$LOGFILE_PATH" ] && [ -f "$LOGFILE_PATH" ]; then',
            '        ORA_COUNT=$(grep -c "ORA-" "$LOGFILE_PATH" 2>/dev/null || echo 0)',
            '        if [ "$ORA_COUNT" -gt 0 ]; then',
            '            echo "[WARNING] Found $ORA_COUNT ORA- errors in log file:"',
            '            grep "ORA-" "$LOGFILE_PATH"',
            "        fi",
            "    fi",
            "    # 可选：发送成功通知",
            '    # echo "Oracle {} success" | mail -s "[OK] Oracle {} {}" dba@example.com'.format(tool, tool, username),
            "else",
            '    echo "[$(date +\\"%Y-%m-%d %H:%M:%S\\")] {} FAILED with return code: ${{RC}}"'.format(tool),
            "    # 扫描日志中的错误信息",
            '    if [ -n "$LOGFILE_PATH" ] && [ -f "$LOGFILE_PATH" ]; then',
            '        echo "[ERROR] Last errors from log:"',
            '        grep "ORA-\\|EXP-\\|IMP-" "$LOGFILE_PATH" | tail -10',
            "    fi",
            "    # 可选：发送失败告警",
            '    # echo "Oracle {} failed with RC=${{RC}}" | mail -s "[FAIL] Oracle {} {}" dba@example.com'.format(tool, tool, username),
            "fi",
            "",
            "exit $RC",
        ])
        return "\n".join(lines)

    def generate_directory_ddl(self) -> str:
        """生成 CREATE OR REPLACE DIRECTORY 的 DDL SQL"""
        directory = self.params.get("directory", "")
        if not directory:
            return ""
        username = self.connection.get("username", "")
        safe_dir = self._safe_sql_id(directory)
        lines = [
            "-- 创建 Directory 对象（需 DBA 权限执行）",
            "CREATE OR REPLACE DIRECTORY {} AS '/path/to/dump';".format(safe_dir),
        ]
        if username:
            safe_user = self._safe_sql_id(username)
            lines.append("GRANT READ, WRITE ON DIRECTORY {} TO {};".format(safe_dir, safe_user))
        return "\n".join(lines)

    def _generate_bat_script(self, command: str) -> str:
        connect_type = self.connection.get("connect_type", "service")
        ident_label = "SID" if connect_type == "sid" else "SERVICE_NAME"
        ident_value = self._get_identifier(connect_type)
        host = self.connection.get("host", "localhost")
        port = self.connection.get("port", 1521)
        username = self.connection.get("username", "")
        tool = self.TOOL_NAME.upper()

        lines = [
            "@echo off",
        ]

        if self.connection.get("ssh_enabled"):
            lines.extend([
                "REM WARNING: SSH tunnel is configured but not supported in .bat scripts.",
                "REM Please use the .sh script on a Linux/WSL environment with SSH tunnel.",
                "",
            ])

        lines.extend([
            "REM ============================================================",
            "REM Oracle {} Script".format(tool),
            "REM Generated: {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "REM Tool: Oracle Backup Command Generator v1.0",
            "REM ============================================================",
            "",
            "REM --- Environment ---",
            "set ORACLE_HOME=C:\\app\\oracle\\product\\19.3.0\\dbhome_1",
            "set PATH=%ORACLE_HOME%\\bin;%PATH%",
            "",
            "REM --- Connection ---",
            "set DB_HOST={}".format(self._sq(host)),
            "set DB_PORT={}".format(self._sq(port)),
            "set DB_USER={}".format(self._sq(username)),
            "set DB_{}={}".format(ident_label, self._sq(ident_value)),
            "set DB_PASS=***  REM 请替换为实际密码",
            "set CONTAINER_MODE={}".format(self.connection.get("container_mode", "")),
            "set PDB_NAME={}".format(self.connection.get("pdb_name", "")),
            "",
            "REM --- Pre-check ---",
            "echo [%date% %time%] Starting {}...".format(tool),
            "",
            "REM Check Oracle service",
            "sc query OracleService%DB_SID% >nul 2>&1",
            "if %ERRORLEVEL% NEQ 0 (",
            "    echo [WARNING] Cannot verify Oracle service status",
            ") else (",
            '    sc query OracleService%DB_SID% | find "RUNNING" >nul 2>&1',
            "    if %ERRORLEVEL% NEQ 0 (",
            "        echo [ERROR] Oracle service is not running!",
            "        exit /b 1",
            "    )",
            ")",
            "",
            "REM --- Execute ---",
        ])

        if self.connection.get("auth_method") == "os":
            lines.append('{} "/ as sysdba" ^'.format(self.TOOL_NAME))
        else:
            ident_var = "DB_{}".format(ident_label)
            lines.append("{} %DB_USER%/%DB_PASS%@%DB_HOST%:%DB_PORT%/%{}% ^".format(self.TOOL_NAME, ident_var))

        for i, p in enumerate(self._parts):
            if i < len(self._parts) - 1:
                lines.append("  {} ^".format(p))
            else:
                lines.append("  {}".format(p))

        lines.extend([
            "",
            "REM --- Result Check ---",
            "if %ERRORLEVEL% EQU 0 (",
            "    echo [%date% %time%] {} completed successfully.".format(tool),
            "    if defined LOGFILE_PATH (",
            '        findstr /C:"ORA-" "%LOGFILE_PATH%" >nul 2>&1',
            "        if %ERRORLEVEL% EQU 0 (",
            '            echo [WARNING] Found ORA- errors in log file',
            '            findstr /C:"ORA-" "%LOGFILE_PATH%"',
            "        )",
            "    )",
            ") else (",
            "    echo [%date% %time%] {} FAILED with return code: %ERRORLEVEL%".format(tool),
            "    if defined LOGFILE_PATH (",
            '        echo [ERROR] Last errors from log:',
            '        findstr /C:"ORA-" /C:"EXP-" /C:"IMP-" "%LOGFILE_PATH%"',
            "    )",
            ")",
            "",
            "exit /b %ERRORLEVEL%",
        ])
        return "\r\n".join(lines)

