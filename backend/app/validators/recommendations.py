"""智能推荐引擎

根据用户参数组合给出优化建议。"""


class Recommendations:
    def get(self, tool: str, params: dict, connection: dict, oracle_version: str) -> list[str]:
        recs = []
        fn = {
            "expdp": self._rec_expdp,
            "exp": self._rec_exp,
            "impdp": self._rec_impdp,
            "imp": self._rec_imp,
        }.get(tool)
        if fn:
            recs.extend(fn(params, connection, oracle_version))
        return recs

    def _rec_expdp(self, p: dict, c: dict, ver: str) -> list[str]:
        recs = []

        # PARALLEL 推荐与 CPU 相关
        parallel = p.get("parallel", 1)
        if parallel <= 1 and p.get("schemas"):
            recs.append("大数据量导出建议设置 PARALLEL=4（根据服务器CPU核心数调整）")

        # COMPRESSION 推荐
        if p.get("compression") == "NONE" or not p.get("compression"):
            recs.append("建议启用 COMPRESSION=ALL 以减少 dump 文件大小和传输时间")

        # LOGFILE 推荐
        if not p.get("logfile"):
            recs.append("建议设置 LOGFILE 参数以便排查导出过程中的问题")

        # DUMPFILE 命名建议
        df = p.get("dumpfile", "")
        if df and "%U" not in df and parallel > 1:
            recs.append(f"DUMPFILE 中缺少 %U 通配符，建议改为 {df.replace('.dmp', '_%U.dmp')}")

        # FLASHBACK 建议
        if not p.get("flashback_scn") and not p.get("flashback_time") and not p.get("consistent"):
            recs.append("生产环境建议使用 FLASHBACK_TIME 或 FLASHBACK_SCN 确保数据一致性")

        return recs

    def _rec_exp(self, p: dict, c: dict, ver: str) -> list[str]:
        recs = []

        if not p.get("direct"):
            recs.append("建议启用 DIRECT=Y 以提高导出速度（直接路径导出）")

        if not p.get("consistent") and p.get("owner"):
            recs.append("导出整个用户的对象时建议启用 CONSISTENT=Y 确保数据一致性")

        if not p.get("logfile"):
            recs.append("建议设置 LOG 参数以便排查问题")

        if p.get("file_size"):
            recs.append("使用 FILESIZE 参数可将导出文件分割，便于传输和管理")

        return recs

    def _rec_impdp(self, p: dict, c: dict, ver: str) -> list[str]:
        recs = []

        if not p.get("table_exists_action") and p.get("schemas"):
            recs.append("目标 Schema 已存在对象时，建议设置 TABLE_EXISTS_ACTION=REPLACE 或 TRUNCATE")

        parallel = p.get("parallel", 1)
        if parallel <= 1:
            recs.append("大数据量导入建议设置 PARALLEL=4 以提高导入速度")

        if p.get("remap_tablespace"):
            recs.append("REMAP_TABLESPACE 支持多个映射，格式：source1:target1,source2:target2")

        if not p.get("logfile"):
            recs.append("建议设置 LOGFILE 参数记录导入详情")

        if p.get("network_link") and not p.get("version"):
            recs.append("NETWORK_LINK 跨版本导入建议设置 VERSION 参数指定源数据库版本")

        return recs

    def _rec_imp(self, p: dict, c: dict, ver: str) -> list[str]:
        recs = []

        if not p.get("commit") and p.get("fromuser"):
            recs.append("大批量数据导入建议启用 COMMIT=Y，避免回滚段不足")

        if p.get("commit") and p.get("buffer", "") == "":
            recs.append("启用 COMMIT 时建议设置较大的 BUFFER 值，如 BUFFER=10485760（10MB）")

        if not p.get("ignore") and p.get("fromuser"):
            recs.append("重复导入时建议设置 IGNORE=Y 跳过已存在的对象")

        if not p.get("logfile"):
            recs.append("建议设置 LOG 参数记录导入详情")

        if p.get("feedback", 0) == 0:
            recs.append("大数据量导入建议设置 FEEDBACK=1000 每1000行显示进度")

        return recs
