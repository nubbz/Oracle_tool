import shlex
from datetime import datetime


class RmanGenerator:

    def generate_backup(self, params: dict) -> dict:
        warnings = []
        recommendations = []
        p = params

        backup_type = p.get("backup_type", "full")
        scope = p.get("scope", "database")
        channel_count = max(1, p.get("channel_count", 1))
        compression = p.get("compression", "NONE")
        encryption = p.get("encryption", "NONE")

        # Validate
        if backup_type == "incremental" and scope == "archivelog":
            warnings.append({"level": "error", "field": "backup_type",
                             "message": "增量备份不适用于归档日志"})

        if backup_type == "incremental" and p.get("incremental_level") not in (0, 1):
            warnings.append({"level": "warning", "field": "incremental_level",
                             "message": "增量级别应为 0 或 1"})

        if encryption != "NONE" and not p.get("encryption_password") and encryption == "PASSWORD":
            warnings.append({"level": "error", "field": "encryption_password",
                             "message": "PASSWORD 加密模式需要设置加密密码"})

        if scope == "tablespace" and not p.get("tablespace_name"):
            warnings.append({"level": "error", "field": "tablespace_name",
                             "message": "表空间备份需要指定表空间名称"})

        if scope == "datafile" and not p.get("datafile_path"):
            warnings.append({"level": "error", "field": "datafile_path",
                             "message": "数据文件备份需要指定数据文件路径"})

        # Recommendations
        if channel_count <= 1 and scope == "database":
            recommendations.append("全库备份建议设置 CHANNEL >= 2 以提高备份速度")
        if compression == "NONE":
            recommendations.append("建议启用压缩以减少备份文件大小（BASIC 模式无需额外 License）")
        if not p.get("tag"):
            recommendations.append("建议设置 TAG 以便管理和恢复时识别备份集")

        # Build RMAN command
        rman_cmds = []
        rman_cmds.append("run {")

        # Allocate channels
        for i in range(1, channel_count + 1):
            fmt = p.get("format_path", "/backup/rman")
            pattern = p.get("format_pattern", "%d_%T_%U")
            rman_cmds.append(f"  allocate channel ch{i} type disk format '{fmt}/{pattern}';")

        # SET options
        if p.get("section_size"):
            rman_cmds.append(f"  set section size {p['section_size']};")

        # Backup command
        if backup_type == "full":
            cmd = "  backup"
        elif backup_type == "incremental":
            level = p.get("incremental_level", 1)
            cmd = f"  backup incremental level {level}"
        elif backup_type == "archivelog":
            cmd = "  backup archivelog"
            if p.get("delete_input"):
                cmd += " delete input"
        else:
            cmd = "  backup"

        # Compress / Encrypt
        if compression != "NONE":
            cmd += " as compressed backupset"
        if encryption != "NONE":
            cmd += f" encrypted"

        # Scope
        if scope == "database":
            cmd += " database"
        elif scope == "tablespace":
            ts = p["tablespace_name"]
            cmd += f" tablespace {ts}"
        elif scope == "datafile":
            df = p["datafile_path"]
            cmd += f" datafile '{df}'"
        elif scope == "controlfile":
            cmd += " current controlfile"
        elif scope == "spfile":
            cmd += " spfile"

        # Options
        if p.get("tag"):
            cmd += f" tag={shlex.quote(p['tag'])}"
        if p.get("skip_offline"):
            cmd += " skip offline"
        if p.get("skip_readonly"):
            cmd += " skip readonly"
        if p.get("skip_inaccessible"):
            cmd += " skip inaccessible"

        cmd += ";"
        rman_cmds.append(cmd)

        # Release channels
        for i in range(1, channel_count + 1):
            rman_cmds.append(f"  release channel ch{i};")

        rman_cmds.append("}")

        rman_script = "\n".join(rman_cmds)

        # Additional RMAN config commands
        config_cmds = []
        if p.get("retention_policy"):
            config_cmds.append(f"CONFIGURE RETENTION POLICY TO {p['retention_policy']};")
        if compression != "NONE":
            config_cmds.append(f"CONFIGURE COMPRESSION ALGORITHM '{compression}';")
        if encryption != "NONE":
            config_cmds.append(f"CONFIGURE ENCRYPTION FOR DATABASE ON;")
            if encryption == "PASSWORD":
                config_cmds.insert(0, f"SET ENCRYPTION ON IDENTIFIED BY {shlex.quote(p.get('encryption_password', ''))} ONLY;")

        if p.get("crosscheck"):
            config_cmds.append("CROSSCHECK BACKUP;")
            config_cmds.append("CROSSCHECK COPY;")
            config_cmds.append("DELETE EXPIRED BACKUP;")
            config_cmds.append("DELETE EXPIRED COPY;")

        if p.get("validate"):
            config_cmds.append("VALIDATE DATABASE;")

        # Build full shell script
        script = self._build_shell_script(rman_script, config_cmds, p)

        return {
            "command": rman_script,
            "script": script,
            "warnings": warnings,
            "recommendations": recommendations,
            "steps": self._build_backup_steps(p, compression, encryption, backup_type, scope, channel_count, config_cmds),
        }

    def _build_backup_steps(self, p, compression, encryption, backup_type, scope, channel_count, config_cmds) -> list[str]:
        steps = []
        fmt = p.get("format_path", "/backup/rman")

        steps.append(f"分配 {channel_count} 个磁盘通道，备份路径: {fmt}")
        if p.get("section_size"):
            steps.append(f"设置多段备份大小: {p['section_size']}")

        type_map = {"full": "全量备份", "incremental": f"增量备份 (Level {p.get('incremental_level', 1)})", "archivelog": "归档日志备份"}
        scope_map = {"database": "整个数据库", "tablespace": f"表空间 {p.get('tablespace_name', '')}", "datafile": f"数据文件 {p.get('datafile_path', '')}", "controlfile": "控制文件", "spfile": "SPFILE"}
        steps.append(f"执行{type_map.get(backup_type, backup_type)}，范围: {scope_map.get(scope, scope)}")

        if compression != "NONE":
            steps.append(f"启用 {compression} 压缩模式")
        if encryption != "NONE":
            enc_map = {"TRANSPARENT": "透明加密 (TDE)", "PASSWORD": "密码加密", "DUAL": "双重加密"}
            steps.append(f"启用{enc_map.get(encryption, encryption)}")

        if p.get("tag"):
            steps.append(f"为备份集打标签: {p['tag']}")

        skip_parts = []
        if p.get("skip_offline"):
            skip_parts.append("离线文件")
        if p.get("skip_readonly"):
            skip_parts.append("只读文件")
        if p.get("skip_inaccessible"):
            skip_parts.append("不可访问文件")
        if skip_parts:
            steps.append(f"跳过: {'、'.join(skip_parts)}")

        if p.get("delete_input"):
            steps.append("备份完成后删除已备份的归档日志")

        steps.append(f"释放所有通道")

        if p.get("retention_policy"):
            steps.append(f"配置保留策略: {p['retention_policy']}")
        if p.get("crosscheck"):
            steps.append("执行交叉检查并清理过期备份记录")
        if p.get("validate"):
            steps.append("验证备份集完整性")

        return steps

    def generate_restore(self, params: dict) -> dict:
        warnings = []
        recommendations = []
        p = params

        restore_type = p.get("restore_type", "database")

        rman_cmds = []
        rman_cmds.append("run {")
        rman_cmds.append("  allocate channel ch1 type disk;")

        if p.get("pitr_time"):
            rman_cmds.append(f"  set until time \"to_date('{p['pitr_time']}','yyyy-mm-dd hh24:mi:ss')\";")
            recommendations.append("时间点恢复需要确保归档日志完整")
        elif p.get("pitr_scn"):
            rman_cmds.append(f"  set until scn {p['pitr_scn']};")
        elif p.get("until_sequence"):
            thread = p.get("until_thread", "1")
            rman_cmds.append(f"  set until sequence {p['until_sequence']} thread {thread};")

        if p.get("from_tag"):
            tag = p["from_tag"]

        if restore_type == "database":
            rman_cmds.append("  restore database;")
            rman_cmds.append("  recover database;")
        elif restore_type == "tablespace":
            ts = p.get("tablespace_name", "")
            rman_cmds.append(f"  restore tablespace {ts};")
            rman_cmds.append(f"  recover tablespace {ts};")
        elif restore_type == "controlfile":
            rman_cmds.append("  restore controlfile from autobackup;")
        elif restore_type == "spfile":
            rman_cmds.append("  restore spfile from autobackup;")
        elif restore_type == "archivelog":
            rman_cmds.append("  restore archivelog all;")

        if p.get("validate"):
            warnings.append({"level": "info", "field": "validate",
                             "message": "验证模式：仅检查备份是否存在，不执行恢复"})

        rman_cmds.append("  release channel ch1;")
        rman_cmds.append("}")

        rman_script = "\n".join(rman_cmds)

        script = self._build_restore_script(rman_script, p)

        return {
            "command": rman_script,
            "script": script,
            "warnings": warnings,
            "recommendations": recommendations,
            "steps": self._build_restore_steps(p, restore_type),
        }

    def _build_restore_steps(self, p, restore_type) -> list[str]:
        steps = []

        steps.append("分配磁盘通道")

        if p.get("pitr_time"):
            steps.append(f"设置恢复目标时间: {p['pitr_time']}（基于时间点恢复）")
        elif p.get("pitr_scn"):
            steps.append(f"设置恢复目标 SCN: {p['pitr_scn']}（基于 SCN 恢复）")
        elif p.get("until_sequence"):
            steps.append(f"设置恢复目标日志序列: {p['until_sequence']} (Thread {p.get('until_thread', '1')})")

        scope_map = {"database": "数据库", "tablespace": f"表空间 {p.get('tablespace_name', '')}", "controlfile": "控制文件", "spfile": "SPFILE", "archivelog": "归档日志"}
        steps.append(f"恢复{scope_map.get(restore_type, restore_type)}")

        if restore_type in ("database", "tablespace"):
            steps.append(f"恢复{scope_map.get(restore_type, restore_type)}（应用归档日志前滚）")

        steps.append("释放通道")
        return steps

    def generate_config(self, params: dict) -> dict:
        settings = params.get("settings", {})
        lines = []
        for key, value in settings.items():
            if value:
                lines.append(f"CONFIGURE {key} TO {value};")
        return {
            "command": "\n".join(lines),
            "script": "",
            "warnings": [],
            "recommendations": [],
            "steps": [f"配置 {key} = {value}" for key, value in settings.items() if value],
        }

    def _build_shell_script(self, rman_script: str, config_cmds: list, p: dict) -> str:
        oracle_home = p.get("oracle_home", "/u01/app/oracle/product/19.3.0/dbhome_1")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        lines = [
            "#!/bin/bash",
            "# ============================================================",
            "# Oracle RMAN Backup Script",
            f"# Generated: {timestamp}",
            "# ============================================================",
            "",
            "# --- Environment ---",
            f"ORACLE_HOME=${{ORACLE_HOME:-{shlex.quote(oracle_home)}}}",
            "export ORACLE_HOME",
            "export PATH=$ORACLE_HOME/bin:$PATH",
            "",
            "# --- Pre-check ---",
            f'echo "[$(date +\\"%Y-%m-%d %H:%M:%S\\")] Starting RMAN backup..."',
            "",
            "PMON_COUNT=$(ps -ef | grep -c '[o]ra_pmon_')",
            "if [ $PMON_COUNT -eq 0 ]; then",
            '    echo "[ERROR] Oracle instance not running!"',
            "    exit 1",
            "fi",
            "",
        ]

        if config_cmds:
            lines.append("# --- RMAN Configuration ---")
            for cmd in config_cmds:
                lines.append(f"rman target / <<EOF")
                lines.append(cmd)
                lines.append("EOF")
            lines.append("")

        lines.extend([
            "# --- Execute Backup ---",
            "rman target / <<'RMANEOF'",
            rman_script,
            "RMANEOF",
            "",
            "# --- Result Check ---",
            "RC=$?",
            'if [ $RC -eq 0 ]; then',
            '    echo "[$(date +\\"%Y-%m-%d %H:%M:%S\\")] RMAN backup completed successfully."',
            "else",
            '    echo "[$(date +\\"%Y-%m-%d %H:%M:%S\\")] RMAN backup FAILED with RC: $RC"',
            "fi",
            "",
            "exit $RC",
        ])
        return "\n".join(lines)

    def _build_restore_script(self, rman_script: str, p: dict) -> str:
        oracle_home = p.get("oracle_home", "/u01/app/oracle/product/19.3.0/dbhome_1")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        lines = [
            "#!/bin/bash",
            "# ============================================================",
            "# Oracle RMAN Restore Script",
            f"# Generated: {timestamp}",
            "# ============================================================",
            "",
            "# --- WARNING ---",
            "# This script performs a RESTORE/RECOVER operation.",
            "# Ensure you have a valid backup before proceeding.",
            "#",
            'read -p "Continue with restore? (yes/no): " CONFIRM',
            'if [ "$CONFIRM" != "yes" ]; then',
            '    echo "Aborted."',
            "    exit 1",
            "fi",
            "",
            f"ORACLE_HOME=${{ORACLE_HOME:-{shlex.quote(oracle_home)}}}",
            "export ORACLE_HOME",
            "export PATH=$ORACLE_HOME/bin:$PATH",
            "",
            "# --- Execute Restore ---",
            "rman target / <<'RMANEOF'",
            rman_script,
            "RMANEOF",
            "",
            "exit $?",
        ]
        return "\n".join(lines)
