import json
from datetime import datetime

from app.generators.expdp_gen import ExpdpGenerator
from app.generators.exp_gen import ExpGenerator
from app.generators.impdp_gen import ImpdpGenerator
from app.generators.imp_gen import ImpGenerator
from app.validators.conflict_engine import ConflictEngine
from app.validators.version_compat import VersionCompat
from app.validators.recommendations import Recommendations


GENERATORS = {
    "expdp": ExpdpGenerator,
    "exp": ExpGenerator,
    "impdp": ImpdpGenerator,
    "imp": ImpGenerator,
}


class CommandService:
    def __init__(self):
        self.conflict_engine = ConflictEngine()
        self.version_compat = VersionCompat()
        self.recommendations = Recommendations()

    def generate(self, tool: str, oracle_version: str, connection: dict, params: dict) -> dict:
        # 1. 参数冲突检测
        conflict_warnings = self.conflict_engine.validate(tool, params, connection)

        # 2. 版本兼容性检查
        version_warnings = self.version_compat.check(tool, params, oracle_version)

        # 3. 智能推荐
        recs = self.recommendations.get(tool, params, connection, oracle_version)

        # 4. 生成命令
        gen_cls = GENERATORS.get(tool)
        if not gen_cls:
            raise ValueError(f"不支持的工具类型: {tool}")

        generator = gen_cls(connection=connection, params=params, oracle_version=oracle_version)
        command = generator.generate_command()
        parfile = generator.generate_parfile()
        script_sh = generator.generate_script("sh")
        script_bat = generator.generate_script("bat")

        # Directory DDL（仅 expdp/impdp）
        directory_ddl = ""
        if tool in ("expdp", "impdp"):
            directory_ddl = generator.generate_directory_ddl()

        all_warnings = conflict_warnings + version_warnings
        has_error = any(w["level"] == "error" for w in all_warnings)

        return {
            "command": command,
            "parfile": parfile,
            "script": script_sh,
            "script_bat": script_bat,
            "warnings": all_warnings,
            "recommendations": recs,
            "has_error": has_error,
            "directory_ddl": directory_ddl,
            "steps": generator.generate_steps(),
        }

    def reverse_generate(self, tool: str, oracle_version: str, connection: dict, params: dict) -> dict:
        """反向生成导入命令：expdp→impdp, exp→imp"""
        if tool == "expdp":
            reverse_tool = "impdp"
            reverse_params = self._map_expdp_to_impdp(params)
        elif tool == "exp":
            reverse_tool = "imp"
            reverse_params = self._map_exp_to_imp(params)
        else:
            raise ValueError(f"工具 {tool} 不支持反向生成导入命令")

        return self.generate(reverse_tool, oracle_version, connection, reverse_params)

    def _map_expdp_to_impdp(self, expdp_params: dict) -> dict:
        """expdp 参数映射为 impdp 参数"""
        impdp = {}
        direct_keys = [
            "directory", "dumpfile", "schemas", "tables", "content",
            "exclude", "include", "parallel", "compression",
            "encryption_password", "version", "flashback_scn", "flashback_time",
        ]
        for key in direct_keys:
            val = expdp_params.get(key)
            if val:
                impdp[key] = val

        # logfile 改名加 _imp 后缀
        logfile = expdp_params.get("logfile", "")
        if logfile:
            if logfile.endswith(".log"):
                impdp["logfile"] = logfile.replace(".log", "_imp.log")
            else:
                impdp["logfile"] = logfile + "_imp"

        return impdp

    def _map_exp_to_imp(self, exp_params: dict) -> dict:
        """exp 参数映射为 imp 参数"""
        imp = {}
        direct_keys = [
            "file", "tables", "buffer", "recordlength", "feedback", "filesize",
        ]
        for key in direct_keys:
            val = exp_params.get(key)
            if val:
                imp[key] = val

        # owner → fromuser
        owner = exp_params.get("owner")
        if owner:
            imp["fromuser"] = owner

        # logfile 改名加 _imp 后缀
        logfile = exp_params.get("logfile", "")
        if logfile:
            if logfile.endswith(".log"):
                imp["logfile"] = logfile.replace(".log", "_imp.log")
            else:
                imp["logfile"] = logfile + "_imp"

        return imp
