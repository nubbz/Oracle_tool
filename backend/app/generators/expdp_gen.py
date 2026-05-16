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
        if p.get("full") and p["full"]:
            self._add_param("FULL", "Y")

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

        # 高级参数
        if p.get("metrics") and p["metrics"]:
            self._add_param("METRICS", "Y")
        if p.get("status"):
            self._add_param("STATUS", p["status"])
        if p.get("data_options"):
            self._add_param("DATA_OPTIONS", p["data_options"])

        # Container Database (CDB)
        if self.connection.get("container_mode") == "CDB":
            self._add_param("CONTAINER", "ALL")

    def _build_steps(self) -> list[str]:
        steps = []
        p = self.params
        added = {k: v for k, v in self._added_params}

        steps.append(self._step_connect())

        tool_label = "数据泵导出 (expdp)"

        if "DIRECTORY" in added:
            steps.append(f"使用 Directory 对象 {added['DIRECTORY']} 定位转储文件目录")
        if "DUMPFILE" in added:
            steps.append(f"将导出数据写入转储文件 {added['DUMPFILE']}")
        if "LOGFILE" in added:
            steps.append(f"日志输出到 {added['LOGFILE']}")

        if "FULL" in added:
            steps.append("执行全库导出")
        elif "SCHEMAS" in added:
            steps.append(f"导出以下 Schema 的数据: {added['SCHEMAS']}")
        elif "TABLES" in added:
            steps.append(f"导出以下表的数据: {added['TABLES']}")
        if "TABLESPACES" in added:
            steps.append(f"导出以下表空间: {added['TABLESPACES']}")

        if "CONTENT" in added:
            content_map = {"DATA_ONLY": "仅数据", "METADATA_ONLY": "仅元数据", "ALL": "全部（数据+元数据）"}
            steps.append(f"导出内容: {content_map.get(added['CONTENT'], added['CONTENT'])}")

        if "QUERY" in added:
            steps.append(f"使用查询条件过滤数据: {added['QUERY']}")
        if "EXCLUDE" in added:
            steps.append(f"排除指定对象: {added['EXCLUDE']}")
        if "INCLUDE" in added:
            steps.append(f"仅包含指定对象: {added['INCLUDE']}")

        if "PARALLEL" in added:
            steps.append(f"启用 {added['PARALLEL']} 个并行工作线程加速导出")
        if "COMPRESSION" in added:
            steps.append(f"启用 {added['COMPRESSION']} 压缩以减小转储文件大小")

        if "ENCRYPTION" in added or "ENCRYPTION_PASSWORD" in added:
            enc_mode = added.get("ENCRYPTION_MODE", "")
            mode_label = f" ({enc_mode})" if enc_mode else ""
            steps.append(f"启用数据加密{mode_label}")

        if "FLASHBACK_SCN" in added:
            steps.append(f"基于 SCN {added['FLASHBACK_SCN']} 实现一致性导出")
        elif "FLASHBACK_TIME" in added:
            steps.append(f"基于时间点 {added['FLASHBACK_TIME']} 实现一致性导出")

        if "VERSION" in added:
            steps.append(f"生成兼容 {added['VERSION']} 版本的转储文件")

        if "FILESIZE" in added:
            steps.append(f"每个转储文件最大 {added['FILESIZE']}，超出后自动分割")

        if "TRANSPORTABLE" in added:
            steps.append("使用传输表空间模式导出")

        if "ESTIMATE" in added:
            steps.append(f"使用 {added['ESTIMATE']} 方式估算导出数据量")

        if "METRICS" in added:
            steps.append("记录导出性能指标")

        if "REUSE_DUMPFILES" in added:
            steps.append("覆盖已存在的转储文件")

        if self.connection.get("container_mode") == "CDB":
            steps.append("以 CDB 模式导出，包含所有 PDB 的数据")

        return steps
