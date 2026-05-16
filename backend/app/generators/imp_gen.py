from app.generators.base import BaseGenerator


class ImpGenerator(BaseGenerator):
    TOOL_NAME = "imp"

    def _build_params(self):
        p = self.params

        # 核心参数
        self._add_param("FILE", p.get("file"))
        self._add_param("LOG", p.get("logfile"))

        # Schema 映射
        if p.get("fromuser"):
            self._add_param("FROMUSER", f'({",".join(p["fromuser"])})')
        if p.get("touser"):
            self._add_param("TOUSER", f'({",".join(p["touser"])})')

        # 表导入
        if p.get("tables"):
            self._add_param("TABLES", f'({",".join(p["tables"])})')

        # 导入控制
        if p.get("commit"):
            self._add_param("COMMIT", "Y")
        if p.get("ignore"):
            self._add_param("IGNORE", "Y")
        if p.get("show"):
            self._add_param("SHOW", "Y")
        if p.get("destroy"):
            self._add_param("DESTROY", "Y")
        if p.get("compile"):
            self._add_param("COMPILE", "Y")

        # 性能参数
        if p.get("buffer"):
            self._add_param("BUFFER", p["buffer"])
        if p.get("streamsize"):
            self._add_param("STREAMSIZE", p["streamsize"])
        if p.get("recordlength", 0) > 0:
            self._add_param("RECORDLENGTH", p["recordlength"])
        if p.get("filesize"):
            self._add_param("FILESIZE", p["filesize"])

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

        # 索引文件
        if p.get("indexfile"):
            self._add_param("INDEXFILE", p["indexfile"])

        # 跳过不可用索引
        if p.get("skip_unusable_indexes"):
            self._add_param("SKIP_UNUSABLE_INDEXES", "Y")

        # 可恢复
        if p.get("resumable"):
            self._add_param("RESUMABLE", "Y")
            if p.get("resumable_name"):
                self._add_param("RESUMABLE_NAME", f'"{p["resumable_name"]}"')
            if p.get("resumable_timeout", 0) > 0:
                self._add_param("RESUMABLE_TIMEOUT", p["resumable_timeout"])

        # TOID 验证
        if p.get("toid_novalidate"):
            self._add_param("TOID_NOVALIDATE", f'({",".join(p["toid_novalidate"])})')
