import re
from typing import Any


class ConflictEngine:
    """参数冲突检测规则引擎"""

    def validate(self, tool: str, params: dict, connection: dict) -> list[dict]:
        warnings = []
        validators = {
            "expdp": self._validate_expdp,
            "exp": self._validate_exp,
            "impdp": self._validate_impdp,
            "imp": self._validate_imp,
        }
        fn = validators.get(tool)
        if fn:
            warnings.extend(fn(params, connection))
        return warnings

    def _validate_expdp(self, p: dict, c: dict) -> list[dict]:
        w = []

        # SCHEMAS 和 TABLES 互斥
        if p.get("schemas") and p.get("tables"):
            w.append({"level": "error", "field": "schemas", "message": "SCHEMAS 和 TABLES 不能同时指定", "suggestion": "导出整个 Schema 使用 SCHEMAS，导出指定表使用 TABLES"})

        # SCHEMAS 和 TABLESPACES 互斥
        if p.get("schemas") and p.get("tablespaces"):
            w.append({"level": "error", "field": "tablespaces", "message": "SCHEMAS 和 TABLESPACES 不能同时指定"})

        # METADATA_ONLY + TABLES 无意义
        if p.get("content") == "METADATA_ONLY" and p.get("tables"):
            w.append({"level": "warning", "field": "content", "message": "CONTENT=METADATA_ONLY 时指定 TABLES 无实际意义", "suggestion": "如只需导出表结构元数据，可保留；如需导出数据请改为 CONTENT=ALL"})

        # DATA_ONLY + TABLESPACES 冲突
        if p.get("content") == "DATA_ONLY" and p.get("tablespaces"):
            w.append({"level": "error", "field": "tablespaces", "message": "CONTENT=DATA_ONLY 不支持 TABLESPACES 参数"})

        # ENCRYPTION + ENCRYPTION_MODE=NONE 矛盾
        if p.get("encryption") and p.get("encryption") != "NONE" and p.get("encryption_mode") == "NONE":
            w.append({"level": "error", "field": "encryption_mode", "message": "ENCRYPTION_MODE=NONE 与启用的加密参数矛盾", "suggestion": "请移除加密参数或将 ENCRYPTION_MODE 设置为其他值"})

        # PARALLEL > 1 但没有 FILESIZE
        if p.get("parallel", 1) > 1 and not p.get("filesize"):
            w.append({"level": "info", "field": "filesize", "message": "并行导出时建议设置 FILESIZE", "suggestion": "设置 FILESIZE 可将 dump 文件分割为多个文件，充分利用并行度，如 FILESIZE=2G"})

        # DUMPFILE 中没有 %U 通配符但 PARALLEL > 1
        if p.get("parallel", 1) > 1 and p.get("dumpfile") and "%U" not in p.get("dumpfile", ""):
            w.append({"level": "warning", "field": "dumpfile", "message": "PARALLEL > 1 时 DUMPFILE 应包含 %U 通配符", "suggestion": "例如：DUMPFILE=backup_%U.dmp，否则并行进程无法写入不同文件"})

        # TRANSPORTABLE 需要配合 TABLESPACES
        if p.get("transportable") and not p.get("tablespaces"):
            w.append({"level": "warning", "field": "transportable", "message": "TRANSPORTABLE 通常需要配合 TABLESPACES 参数", "suggestion": "指定需要传输的表空间列表"})

        # DIRECTORY 未设置
        if not p.get("directory"):
            w.append({"level": "error", "field": "directory", "message": "DIRECTORY 为必填参数", "suggestion": "请指定 Oracle Directory 对象名称，如 DP_DIR"})

        # FLASHBACK_SCN 和 FLASHBACK_TIME 不能同时指定
        if p.get("flashback_scn") and p.get("flashback_time"):
            w.append({"level": "error", "field": "flashback_scn", "message": "FLASHBACK_SCN 和 FLASHBACK_TIME 不能同时指定", "suggestion": "选择其中一种闪回方式"})

        # FILESIZE 格式校验
        if p.get("filesize") and not re.match(r'^\d+[BKMGT]$', p["filesize"], re.IGNORECASE):
            w.append({"level": "error", "field": "filesize", "message": "FILESIZE 格式错误", "suggestion": "格式为 数字+单位，如 2G、500M、1024K"})

        # QUERY 中包含单引号提示
        if p.get("query") and "'" in p["query"]:
            w.append({"level": "info", "field": "query", "message": "QUERY 中包含单引号，命令行中需正确转义", "suggestion": "在 parfile 中使用可避免转义问题"})

        # DIRECTORY 建议大写
        if p.get("directory") and p["directory"] != p["directory"].upper():
            w.append({"level": "info", "field": "directory", "message": "DIRECTORY 建议使用大写", "suggestion": f"建议改为 {p['directory'].upper()}"})

        # FULL + SCHEMAS/TABLES 互斥
        if p.get("full") and (p.get("schemas") or p.get("tables")):
            w.append({"level": "error", "field": "full", "message": "FULL 不能与 SCHEMAS/TABLES 同时指定", "suggestion": "全库导出请移除 SCHEMAS/TABLES"})

        return w

    def _validate_exp(self, p: dict, c: dict) -> list[dict]:
        w = []

        # OWNER 和 TABLES 互斥
        if p.get("owner") and p.get("tables"):
            w.append({"level": "error", "field": "owner", "message": "OWNER 和 TABLES 不能同时指定", "suggestion": "导出整个用户的对象使用 OWNER，导出指定表使用 TABLES"})

        # DIRECT + CONSISTENT + QUERY 性能警告
        if p.get("direct") and p.get("consistent") and p.get("query"):
            w.append({"level": "warning", "field": "direct", "message": "DIRECT=Y + CONSISTENT=Y + QUERY 可能显著影响性能", "suggestion": "大数据量导出时考虑移除 DIRECT 或 CONSISTENT"})

        # FILE 未设置
        if not p.get("file"):
            w.append({"level": "error", "field": "file", "message": "FILE 为必填参数", "suggestion": "请指定导出文件路径，如 expdat.dmp"})

        # RESUMABLE 超时值
        if p.get("resumable") and p.get("resumable_timeout", 0) <= 0:
            w.append({"level": "info", "field": "resumable_timeout", "message": "启用 RESUMABLE 建议设置超时时间", "suggestion": "设置 RESUMABLE_TIMEOUT=7200（2小时）"})

        return w

    def _validate_impdp(self, p: dict, c: dict) -> list[dict]:
        w = []

        # TABLE_EXISTS_ACTION 未设置但有 SCHEMAS
        if not p.get("table_exists_action") and p.get("schemas"):
            w.append({"level": "info", "field": "table_exists_action", "message": "导入 Schema 时建议设置 TABLE_EXISTS_ACTION", "suggestion": "REPLACE=覆盖已存在表, APPEND=追加数据, TRUNCATE=清空后导入, SKIP=跳过"})

        # NETWORK_LINK + DUMPFILE 无意义
        if p.get("network_link") and p.get("dumpfile"):
            w.append({"level": "warning", "field": "dumpfile", "message": "NETWORK_LINK 模式下 DUMPFILE 通常不需要", "suggestion": "网络导入模式下数据直接通过网络传输，无需 dump 文件。如需保存可保留"})

        # SCHEMAS + REMAP_SCHEMA 冲突
        if p.get("schemas") and p.get("remap_schema"):
            w.append({"level": "warning", "field": "schemas", "message": "同时指定 SCHEMAS 和 REMAP_SCHEMA 时，SCHEMAS 应为目标 Schema", "suggestion": "例如 REMAP_SCHEMA=source:target，SCHEMAS=target"})

        # SQLFILE + 其他导入操作冲突
        if p.get("sqlfile"):
            if p.get("table_exists_action"):
                w.append({"level": "warning", "field": "sqlfile", "message": "SQLFILE 模式只生成DDL不执行导入", "suggestion": "TABLE_EXISTS_ACTION 在 SQLFILE 模式下无效"})

        # DIRECTORY 未设置
        if not p.get("directory") and not p.get("network_link"):
            w.append({"level": "error", "field": "directory", "message": "DIRECTORY 为必填参数（NETWORK_LINK 模式除外）", "suggestion": "请指定 Oracle Directory 对象名称"})

        # FLASHBACK_SCN 和 FLASHBACK_TIME 不能同时指定
        if p.get("flashback_scn") and p.get("flashback_time"):
            w.append({"level": "error", "field": "flashback_scn", "message": "FLASHBACK_SCN 和 FLASHBACK_TIME 不能同时指定"})

        # PARALLEL > 1 + PARTITION_OPTIONS=DEPARTITION
        if p.get("parallel", 1) > 1 and p.get("partition_options") == "DEPARTITION":
            w.append({"level": "warning", "field": "parallel", "message": "DEPARTITION 模式下 PARALLEL 可能导致问题", "suggestion": "考虑在分区表较多时降低 PARALLEL 值"})

        # REMAP_SCHEMA 格式校验
        if p.get("remap_schema") and ":" not in p["remap_schema"]:
            w.append({"level": "error", "field": "remap_schema", "message": "REMAP_SCHEMA 格式错误，必须为 source:target", "suggestion": "例如 REMAP_SCHEMA=SCOTT:SCOTT_NEW"})

        # REMAP_TABLE 格式校验
        if p.get("remap_table") and ":" not in p["remap_table"]:
            w.append({"level": "error", "field": "remap_table", "message": "REMAP_TABLE 格式错误，必须为 source_table:target_table", "suggestion": "例如 REMAP_TABLE=EMP:EMP_BAK"})

        # REMAP_TABLESPACE 格式校验
        if p.get("remap_tablespace"):
            for mapping in p["remap_tablespace"].split(","):
                if ":" not in mapping.strip():
                    w.append({"level": "error", "field": "remap_tablespace", "message": f"REMAP_TABLESPACE 格式错误：'{mapping.strip()}' 缺少冒号", "suggestion": "每个映射格式为 old:new，多个用逗号分隔"})

        # PARALLEL + DUMPFILE %U（impdp 导入也适用）
        if p.get("parallel", 1) > 1 and p.get("dumpfile") and "%U" not in p.get("dumpfile", ""):
            w.append({"level": "warning", "field": "dumpfile", "message": "PARALLEL > 1 时 DUMPFILE 应包含 %U 通配符", "suggestion": "例如：DUMPFILE=backup_%U.dmp"})

        # QUERY 中包含单引号提示
        if p.get("query") and "'" in p["query"]:
            w.append({"level": "info", "field": "query", "message": "QUERY 中包含单引号，命令行中需正确转义"})

        # DIRECTORY 建议大写
        if p.get("directory") and p["directory"] != p["directory"].upper():
            w.append({"level": "info", "field": "directory", "message": "DIRECTORY 建议使用大写", "suggestion": f"建议改为 {p['directory'].upper()}"})

        return w

    def _validate_imp(self, p: dict, c: dict) -> list[dict]:
        w = []

        # FROMUSER 没有 TOUSER
        if p.get("fromuser") and not p.get("touser"):
            w.append({"level": "warning", "field": "touser", "message": "指定了 FROMUSER 但未指定 TOUSER", "suggestion": "如需将对象导入到不同用户，请设置 TOUSER；否则对象将导入 FROMUSER 对应用户"})

        # FROMUSER 和 TABLES 互斥
        if p.get("fromuser") and p.get("tables"):
            w.append({"level": "error", "field": "fromuser", "message": "FROMUSER 和 TABLES 不能同时指定", "suggestion": "按用户导入使用 FROMUSER/TOUSER，按表导入使用 TABLES"})

        # COMMIT + IGNORE=N
        if p.get("commit") and not p.get("ignore"):
            w.append({"level": "info", "field": "ignore", "message": "启用 COMMIT 时建议同时设置 IGNORE=Y", "suggestion": "IGNORE=Y 可跳过已存在的对象错误，配合 COMMIT 实现大批量导入"})

        # SHOW + 其他操作参数
        if p.get("show"):
            if p.get("commit"):
                w.append({"level": "warning", "field": "show", "message": "SHOW=Y 模式只显示DDL不执行导入", "suggestion": "COMMIT 参数在 SHOW 模式下无效"})

        # DESTROY 警告
        if p.get("destroy"):
            w.append({"level": "warning", "field": "destroy", "message": "DESTROY=Y 将删除并重建表空间数据文件", "suggestion": "此操作不可逆，请确认目标表空间可以安全删除"})

        # FILE 未设置
        if not p.get("file"):
            w.append({"level": "error", "field": "file", "message": "FILE 为必填参数", "suggestion": "请指定导入文件路径"})

        return w
