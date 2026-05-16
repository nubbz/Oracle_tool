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

    def _build_steps(self) -> list[str]:
        steps = []
        added = {k: v for k, v in self._added_params}

        steps.append(self._step_connect())

        if "FILE" in added:
            steps.append(f"从导出文件 {added['FILE']} 导入数据")
        if "LOG" in added:
            steps.append(f"日志输出到 {added['LOG']}")

        if "FROMUSER" in added:
            steps.append(f"导入源 Schema: {added['FROMUSER']}")
        if "TOUSER" in added:
            steps.append(f"导入到目标 Schema: {added['TOUSER']}")
        elif "TABLES" in added:
            steps.append(f"导入以下表: {added['TABLES']}")

        if "COMMIT" in added:
            steps.append("每批数据提交一次，减少事务回滚风险")
        if "IGNORE" in added:
            steps.append("忽略对象已存在等非致命错误继续导入")
        if "SHOW" in added:
            steps.append("仅显示 SQL 语句，不执行实际导入")
        if "COMPILE" in added:
            steps.append("导入后重新编译所有 PL/SQL 对象")

        if "BUFFER" in added:
            steps.append(f"设置数据缓冲区大小: {added['BUFFER']}")

        if "INDEXFILE" in added:
            steps.append(f"将索引创建语句写入文件 {added['INDEXFILE']}")

        if "ROWS" in added and added["ROWS"] == "N":
            steps.append("仅导入元数据（不导入数据行）")

        skip_labels = {"INDEXES": "索引", "CONSTRAINTS": "约束", "GRANTS": "权限", "TRIGGERS": "触发器"}
        for key, label in skip_labels.items():
            if key in added and added[key] == "N":
                steps.append(f"不导入{label}")

        if "STATISTICS" in added:
            steps.append(f"统计信息处理方式: {added['STATISTICS']}")

        if "FILESIZE" in added:
            steps.append(f"每个文件大小: {added['FILESIZE']}")

        return steps
