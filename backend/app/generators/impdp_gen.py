from app.generators.base import BaseGenerator


class ImpdpGenerator(BaseGenerator):
    TOOL_NAME = "impdp"

    def _build_params(self):
        p = self.params

        # 核心参数
        self._add_param("DIRECTORY", p.get("directory"))
        self._add_param("DUMPFILE", p.get("dumpfile"))
        self._add_param("LOGFILE", p.get("logfile"))

        # 导入范围
        if p.get("schemas"):
            self._add_param("SCHEMAS", p["schemas"])
        if p.get("tables"):
            self._add_param("TABLES", p["tables"])

        # 内容过滤
        if p.get("content") and p["content"] != "ALL":
            self._add_param("CONTENT", p["content"])
        if p.get("exclude"):
            for ex in p["exclude"]:
                self._add_param("EXCLUDE", f'"{ex}"')
        if p.get("include"):
            for inc in p["include"]:
                self._add_param("INCLUDE", f'"{inc}"')

        # 映射参数
        if p.get("remap_schema"):
            self._add_param("REMAP_SCHEMA", p["remap_schema"])
        if p.get("remap_tablespace"):
            self._add_param("REMAP_TABLESPACE", p["remap_tablespace"])
        if p.get("remap_datafile"):
            self._add_param("REMAP_DATAFILE", p["remap_datafile"])

        # 表存在时的处理
        if p.get("table_exists_action"):
            self._add_param("TABLE_EXISTS_ACTION", p["table_exists_action"])

        # 性能参数
        if p.get("parallel", 1) > 1:
            self._add_param("PARALLEL", p["parallel"])

        # 压缩
        if p.get("compression") and p["compression"] != "NONE":
            self._add_param("COMPRESSION", p["compression"])

        # Transform
        if p.get("transform"):
            self._add_param("TRANSFORM", f'"{p["transform"]}"')

        # 生成SQL文件
        if p.get("sqlfile"):
            self._add_param("SQLFILE", p["sqlfile"])

        # 分区选项
        if p.get("partition_options"):
            self._add_param("PARTITION_OPTIONS", p["partition_options"])

        # 数据选项
        if p.get("data_options"):
            self._add_param("DATA_OPTIONS", p["data_options"])

        # 禁用归档日志
        if p.get("disable_archive_logging"):
            self._add_param("DISABLE_ARCHIVE_LOGGING", "Y")

        # 加密
        if p.get("encryption_password"):
            self._add_param("ENCRYPTION_PASSWORD", p["encryption_password"])

        # 版本兼容性
        if p.get("version"):
            self._add_param("VERSION", p["version"])

        # Flashback
        if p.get("flashback_scn"):
            self._add_param("FLASHBACK_SCN", p["flashback_scn"])
        if p.get("flashback_time"):
            self._add_param("FLASHBACK_TIME", f'"{p["flashback_time"]}"')

        # 网络导入
        if p.get("network_link"):
            self._add_param("NETWORK_LINK", p["network_link"])

        # 覆盖参数
        if p.get("reuse_datafiles"):
            self._add_param("REUSE_DATAFILES", "Y")
        if p.get("reuse_dumpfiles"):
            self._add_param("REUSE_DUMPFILES", "Y")

        # 作业名
        if p.get("job_name"):
            self._add_param("JOB_NAME", p["job_name"])

        # 日志时间戳
        if p.get("logtime"):
            self._add_param("LOGTIME", p["logtime"])

        # 性能指标
        if p.get("metrics"):
            self._add_param("METRICS", "Y")

        # 表名重映射
        if p.get("remap_table"):
            self._add_param("REMAP_TABLE", p["remap_table"])

        # Container Database (CDB)
        if self.connection.get("container_mode") == "CDB":
            self._add_param("CONTAINER", "ALL")

        # 高级参数
        if p.get("full") and p["full"]:
            self._add_param("FULL", "Y")
        if p.get("status"):
            self._add_param("STATUS", p["status"])
        if p.get("views_as_tables"):
            self._add_param("VIEWS_AS_TABLES", p["views_as_tables"])

    def _build_steps(self) -> list[str]:
        steps = []
        p = self.params
        added = {k: v for k, v in self._added_params}

        steps.append(self._step_connect())

        if "DIRECTORY" in added:
            steps.append(f"使用 Directory 对象 {added['DIRECTORY']} 定位转储文件目录")
        if "DUMPFILE" in added:
            steps.append(f"从转储文件 {added['DUMPFILE']} 导入数据")
        if "LOGFILE" in added:
            steps.append(f"日志输出到 {added['LOGFILE']}")

        if "FULL" in added:
            steps.append("执行全库导入")
        elif "SCHEMAS" in added:
            steps.append(f"导入以下 Schema 的数据: {added['SCHEMAS']}")
        elif "TABLES" in added:
            steps.append(f"导入以下表的数据: {added['TABLES']}")

        if "CONTENT" in added:
            content_map = {"DATA_ONLY": "仅数据", "METADATA_ONLY": "仅元数据", "ALL": "全部（数据+元数据）"}
            steps.append(f"导入内容: {content_map.get(added['CONTENT'], added['CONTENT'])}")

        if "REMAP_SCHEMA" in added:
            steps.append(f"重映射 Schema: {added['REMAP_SCHEMA']}")
        if "REMAP_TABLESPACE" in added:
            steps.append(f"重映射表空间: {added['REMAP_TABLESPACE']}")
        if "REMAP_TABLE" in added:
            steps.append(f"重映射表名: {added['REMAP_TABLE']}")
        if "REMAP_DATAFILE" in added:
            steps.append(f"重映射数据文件路径: {added['REMAP_DATAFILE']}")

        if "TABLE_EXISTS_ACTION" in added:
            action_map = {"SKIP": "跳过", "APPEND": "追加数据", "TRUNCATE": "先清空再导入", "REPLACE": "替换表"}
            steps.append(f"目标表已存在时: {action_map.get(added['TABLE_EXISTS_ACTION'], added['TABLE_EXISTS_ACTION'])}")

        if "EXCLUDE" in added:
            steps.append(f"排除指定对象: {added['EXCLUDE']}")
        if "INCLUDE" in added:
            steps.append(f"仅包含指定对象: {added['INCLUDE']}")

        if "PARALLEL" in added:
            steps.append(f"启用 {added['PARALLEL']} 个并行工作线程加速导入")
        if "COMPRESSION" in added:
            steps.append(f"启用 {added['COMPRESSION']} 解压缩")

        if "SQLFILE" in added:
            steps.append(f"将 DDL SQL 语句写入文件 {added['SQLFILE']}（不执行实际导入）")

        if "NETWORK_LINK" in added:
            steps.append(f"通过数据库链路 {added['NETWORK_LINK']} 直接导入远程数据")

        if "ENCRYPTION_PASSWORD" in added:
            steps.append("使用密码解密转储文件")

        if "FLASHBACK_SCN" in added:
            steps.append(f"基于 SCN {added['FLASHBACK_SCN']} 实现一致性导入")
        elif "FLASHBACK_TIME" in added:
            steps.append(f"基于时间点 {added['FLASHBACK_TIME']} 实现一致性导入")

        if "VERSION" in added:
            steps.append(f"导入兼容版本: {added['VERSION']}")

        if "PARTITION_OPTIONS" in added:
            steps.append(f"分区导入选项: {added['PARTITION_OPTIONS']}")

        if "TRANSFORM" in added:
            steps.append(f"应用转换规则: {added['TRANSFORM']}")

        if "DISABLE_ARCHIVE_LOGGING" in added:
            steps.append("禁用归档日志以提升导入性能")

        if "METRICS" in added:
            steps.append("记录导入性能指标")

        if "REUSE_DATAFILES" in added:
            steps.append("重用已有数据文件")

        if self.connection.get("container_mode") == "CDB":
            steps.append("以 CDB 模式导入，包含所有 PDB 的数据")

        return steps
