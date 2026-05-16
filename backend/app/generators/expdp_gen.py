from app.generators.base import BaseGenerator


class ExpdpGenerator(BaseGenerator):
    TOOL_NAME = "expdp"

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
        if p.get("tablespaces"):
            self._add_param("TABLESPACES", p["tablespaces"])

        # 内容过滤
        if p.get("content") and p["content"] != "ALL":
            self._add_param("CONTENT", p["content"])
        if p.get("query"):
            self._add_param("QUERY", f'"{p["query"]}"')
        if p.get("exclude"):
            for ex in p["exclude"]:
                self._add_param("EXCLUDE", f'"{ex}"')
        if p.get("include"):
            for inc in p["include"]:
                self._add_param("INCLUDE", f'"{inc}"')

        # 性能参数
        if p.get("parallel", 1) > 1:
            self._add_param("PARALLEL", p["parallel"])
        if p.get("filesize"):
            self._add_param("FILESIZE", p["filesize"])

        # 压缩
        if p.get("compression") and p["compression"] != "NONE":
            self._add_param("COMPRESSION", p["compression"])

        # 覆盖已有文件
        if p.get("reuse_dumpfiles"):
            self._add_param("REUSE_DUMPFILES", "Y")

        # 版本兼容性
        if p.get("version"):
            self._add_param("VERSION", p["version"])

        # Flashback
        if p.get("flashback_scn"):
            self._add_param("FLASHBACK_SCN", p["flashback_scn"])
        if p.get("flashback_time"):
            self._add_param("FLASHBACK_TIME", f'"{p["flashback_time"]}"')

        # 加密
        if p.get("encryption") and p["encryption"] != "NONE":
            self._add_param("ENCRYPTION", p["encryption"])
        if p.get("encryption_password"):
            self._add_param("ENCRYPTION_PASSWORD", p["encryption_password"])
        if p.get("encryption_mode"):
            self._add_param("ENCRYPTION_MODE", p["encryption_mode"])
        if p.get("encryption_columns_only"):
            self._add_param("ENCRYPTION_COLUMNS_ONLY", ",".join(p["encryption_columns_only"]))

        # 传输表空间
        if p.get("transportable"):
            self._add_param("TRANSPORTABLE", "ALWAYS")
        if p.get("transport_full_check"):
            self._add_param("TRANSPORT_FULL_CHECK", "Y")

        # 作业名
        if p.get("job_name"):
            self._add_param("JOB_NAME", p["job_name"])

        # 空间估算
        if p.get("estimate"):
            self._add_param("ESTIMATE", p["estimate"])

        # Container Database (CDB)
        if self.connection.get("container_mode") == "CDB":
            self._add_param("CONTAINER", "ALL")
