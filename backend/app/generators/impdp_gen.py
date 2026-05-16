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
