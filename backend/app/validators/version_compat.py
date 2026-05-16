"""Oracle 版本兼容性检查

定义各 Oracle 版本支持的参数，不支持的参数将被标记为警告。
版本顺序: 10g < 11g < 12c < 19c < 21c < 23c
"""

from typing import Any

VERSION_ORDER = ["10g", "11g", "12c", "19c", "21c", "23c"]

# 参数最低支持版本（该版本及以上才支持）
# 格式: {tool: {param: min_version}}
MIN_VERSION_PARAMS = {
    "expdp": {
        "encryption": "11g",
        "encryption_password": "11g",
        "encryption_mode": "11g",
        "encryption_columns_only": "11g",
        "compression": "11g",
        "reuse_dumpfiles": "11g",
        "transportable": "12c",
        "transport_full_check": "12c",
        "version": "11g",
        "flashback_scn": "10g",
        "flashback_time": "10g",
        "data_options": "11g",
        "disable_archive_logging": "12c",
        "container": "12c",
    },
    "exp": {
        "resumable": "9i",
        "resumable_name": "9i",
        "resumable_timeout": "9i",
        "object_consistent": "10g",
    },
    "impdp": {
        "remap_schema": "10g",
        "remap_tablespace": "10g",
        "remap_datafile": "10g",
        "table_exists_action": "10g",
        "network_link": "10g",
        "encryption_password": "11g",
        "version": "11g",
        "flashback_scn": "10g",
        "flashback_time": "10g",
        "transform": "11g",
        "sqlfile": "10g",
        "partition_options": "11g",
        "data_options": "11g",
        "disable_archive_logging": "12c",
        "reuse_datafiles": "10g",
        "reuse_dumpfiles": "11g",
        "compression": "11g",
        "transportable": "12c",
        "container": "12c",
    },
    "imp": {
        "streamsize": "10g",
        "resumable": "9i",
        "resumable_name": "9i",
        "resumable_timeout": "9i",
        "skip_unusable_indexes": "10g",
        "toid_novalidate": "8i",
    },
}

# 参数最高支持版本（该版本及以上不支持，已废弃）
DEPRECATED_PARAMS = {
    "exp": {
        "buffer": "23c",
        "recordlength": "23c",
    },
    "imp": {
        "buffer": "23c",
        "recordlength": "23c",
        "streamsize": "23c",
        "compile": "23c",
        "destroy": "23c",
    },
}


class VersionCompat:
    def check(self, tool: str, params: dict, oracle_version: str) -> list[dict]:
        warnings = []

        if oracle_version not in VERSION_ORDER:
            return warnings

        version_idx = VERSION_ORDER.index(oracle_version)

        # 检查最低版本要求
        min_params = MIN_VERSION_PARAMS.get(tool, {})
        for param, min_ver in min_params.items():
            if not self._has_value(params.get(param)):
                continue
            if min_ver not in VERSION_ORDER:
                continue
            min_idx = VERSION_ORDER.index(min_ver)
            if version_idx < min_idx:
                warnings.append({
                    "level": "error",
                    "field": param,
                    "message": f"参数 {param.upper()} 需要 Oracle {min_ver} 或更高版本",
                    "suggestion": f"当前版本为 {oracle_version}，请升级数据库或移除该参数",
                })

        # 检查废弃参数
        dep_params = DEPRECATED_PARAMS.get(tool, {})
        for param, max_ver in dep_params.items():
            if not self._has_value(params.get(param)):
                continue
            if max_ver not in VERSION_ORDER:
                continue
            max_idx = VERSION_ORDER.index(max_ver)
            if version_idx >= max_idx:
                warnings.append({
                    "level": "warning",
                    "field": param,
                    "message": f"参数 {param.upper()} 在 Oracle {max_ver} 中已废弃",
                    "suggestion": "建议使用替代方案或移除该参数",
                })

        return warnings

    def _has_value(self, value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (str, int, float)):
            return value != "" and value != 0
        if isinstance(value, list):
            return len(value) > 0
        return True
