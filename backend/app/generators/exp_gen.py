from app.generators.base import BaseGenerator


class ExpGenerator(BaseGenerator):
    TOOL_NAME = "exp"

    def _build_params(self):
        p = self.params

        # 核心参数
        self._add_param("FILE", p.get("file"))
        self._add_param("LOG", p.get("logfile"))

        # 导入范围
        if p.get("owner"):
            self._add_param("OWNER", f'({",".join(p["owner"])})')
        if p.get("tables"):
            self._add_param("TABLES", f'({",".join(p["tables"])})')

        # 查询条件
        if p.get("query"):
            self._add_param("QUERY", f'"{p["query"]}"')

        # 性能参数
        if p.get("direct"):
            self._add_param("DIRECT", "Y")
        if p.get("compress"):
            self._add_param("COMPRESS", "Y")
        if p.get("consistent"):
            self._add_param("CONSISTENT", "Y")
        if p.get("buffer"):
            self._add_param("BUFFER", p["buffer"])
        if p.get("recordlength", 0) > 0:
            self._add_param("RECORDLENGTH", p["recordlength"])
        if p.get("file_size"):
            self._add_param("FILESIZE", p["file_size"])

        # 统计信息
        if p.get("statistics"):
            self._add_param("STATISTICS", p["statistics"])

        # 对象过滤
        if not p.get("rows", True):
            self._add_param("ROWS", "N")
        if not p.get("indexes", True):
            self._add_param("INDEXES", "N")
        if not p.get("constraints", True):
            self._add_param("CONSTRAINTS", "N")
        if not p.get("grants", True):
            self._add_param("GRANTS", "N")
        if not p.get("triggers", True):
            self._add_param("TRIGGERS", "N")

        # 反馈
        if p.get("feedback", 0) > 0:
            self._add_param("FEEDBACK", p["feedback"])

        # 可恢复
        if p.get("resumable"):
            self._add_param("RESUMABLE", "Y")
            if p.get("resumable_name"):
                self._add_param("RESUMABLE_NAME", f'"{p["resumable_name"]}"')
            if p.get("resumable_timeout", 0) > 0:
                self._add_param("RESUMABLE_TIMEOUT", p["resumable_timeout"])

        # 对象一致性
        if p.get("object_consistent"):
            self._add_param("OBJECT_CONSISTENT", "Y")
