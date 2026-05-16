import shlex
from datetime import datetime


class SqlldrGenerator:

    def generate(self, params: dict) -> dict:
        warnings = []
        recommendations = []
        p = params

        if not p.get("table_name"):
            warnings.append({"level": "error", "field": "table_name", "message": "目标表名不能为空"})
        if not p.get("data_file"):
            warnings.append({"level": "error", "field": "data_file", "message": "数据文件路径不能为空"})
        if not p.get("columns"):
            warnings.append({"level": "warning", "field": "columns",
                             "message": "未指定列定义，将自动推断",
                             "suggestion": "建议显式指定列定义以避免数据错位"})

        if p.get("direct_path") and p.get("load_method") in ("replace", "truncate"):
            recommendations.append("DIRECT PATH + REPLACE/TRUNCATE 组合效率最高")

        if not p.get("log_file"):
            recommendations.append("建议设置 LOG 文件以便排查加载错误")

        # Build control file
        ctrl_lines = [
            f"-- SQL*Loader Control File",
            f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"OPTIONS (SKIP={p.get('skip_rows', 0)})",
            f"LOAD DATA",
        ]

        method = p.get("load_method", "INSERT").upper()
        if p.get("data_file"):
            ctrl_lines.append(f"INFILE {shlex.quote(p['data_file'])}")
        ctrl_lines.append(f"INTO TABLE {p.get('table_name', 'UNKNOWN')}")
        ctrl_lines.append(f"{method}")

        terminated = p.get("fields_terminated_by", ",")
        enclosed = p.get("fields_optionally_enclosed_by", '"')
        lines_term = p.get("lines_terminated_by", "\\n")

        field_clause = f'FIELDS TERMINATED BY {shlex.quote(terminated)}'
        if enclosed:
            field_clause += f' OPTIONALLY ENCLOSED BY {shlex.quote(enclosed)}'
        ctrl_lines.append(field_clause)

        if p.get("columns"):
            ctrl_lines.append(f"({p['columns']})")
        else:
            ctrl_lines.append("(FIELDS_HERE)")

        control_file = "\n".join(ctrl_lines)

        # Build sqlldr command
        parts = ["sqlldr"]

        # Connection
        username = p.get("username", "")
        password = p.get("password", "")
        host = p.get("host", "localhost")
        port = p.get("port", 1521)
        connect_type = p.get("connect_type", "service")
        ident = p.get("service_name", "") if connect_type == "service" else p.get("sid", "orcl")

        if username and password:
            parts.append(f'{username}/"{password}"@{host}:{port}/{ident}')

        # Control file
        ctrl_filename = (p.get("data_file", "load") + ".ctl").replace(".dat.ctl", ".ctl").replace(".csv.ctl", ".ctl")
        parts.append(f"control={shlex.quote(ctrl_filename)}")

        # Log/Bad/Discard
        if p.get("log_file"):
            parts.append(f"log={shlex.quote(p['log_file'])}")
        if p.get("bad_file"):
            parts.append(f"bad={shlex.quote(p['bad_file'])}")
        if p.get("discard_file"):
            parts.append(f"discard={shlex.quote(p['discard_file'])}")

        # Performance
        if p.get("direct_path"):
            parts.append("direct=true")
        if p.get("parallel"):
            parts.append("parallel=true")
        if p.get("bindsize"):
            parts.append(f"bindsize={p['bindsize']}")
        if p.get("rows"):
            parts.append(f"rows={p['rows']}")
        if p.get("errors"):
            parts.append(f"errors={p['errors']}")
        if p.get("discardmax"):
            parts.append(f"discardmax={p['discardmax']}")

        command = " \\\n  ".join(parts)

        # Build shell script
        script = self._build_script(command, control_file, ctrl_filename, p)

        return {
            "command": command,
            "control_file": control_file,
            "script": script,
            "warnings": warnings,
            "recommendations": recommendations,
        }

    def _build_script(self, command: str, control_file: str, ctrl_filename: str, p: dict) -> str:
        oracle_home = p.get("oracle_home", "/u01/app/oracle/product/19.3.0/dbhome_1")
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        lines = [
            "#!/bin/bash",
            "# ============================================================",
            "# Oracle SQL*Loader Script",
            f"# Generated: {ts}",
            "# ============================================================",
            "",
            f"ORACLE_HOME=${{ORACLE_HOME:-{shlex.quote(oracle_home)}}}",
            "export ORACLE_HOME",
            "export PATH=$ORACLE_HOME/bin:$PATH",
            "",
            "# --- Write Control File ---",
            f"cat > {shlex.quote(ctrl_filename)} << 'CTLEOF'",
            control_file,
            "CTLEOF",
            "",
            "# --- Execute ---",
            f"echo '[$(date +\"%Y-%m-%d %H:%M:%S\")] Starting SQL*Loader...'",
            command,
            "",
            "RC=$?",
            'if [ $RC -eq 0 ]; then',
            '    echo "[$(date +\\"%Y-%m-%d %H:%M:%S\\")] SQL*Loader completed successfully."',
            "else",
            '    echo "[$(date +\\"%Y-%m-%d %H:%M:%S\\")] SQL*Loader FAILED with RC: $RC"',
            "fi",
            "",
            "exit $RC",
        ]
        return "\n".join(lines)
