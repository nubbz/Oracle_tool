import os

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.installer import InstallRequest, InstallResponse, FLAG_MAP, ASM_FIELDS, RAC_FIELDS
from app.models.history import History
from app.api.v1.auth import get_current_user

router = APIRouter()


def _build_command(req: InstallRequest) -> tuple[str, list[str], list[str]]:
    parts = ["./OracleShellInstall"]
    tags = []
    steps = []
    data = req.model_dump()
    mode = req.mode

    mode_label = {"single": "单机", "standalone": "单机 ASM (Standalone)", "rac": "RAC 集群"}
    steps.append(f"安装模式: {mode_label.get(mode, mode)}")

    version_labels = {"11": "Oracle 11g R2", "12": "Oracle 12c R2", "19": "Oracle 19c", "21": "Oracle 21c", "26": "Oracle 23c"}

    param_labels = {
        "db_version": "安装 {value} 版本数据库",
        "hostname": "目标主机名: {value}",
        "oracle_user": "使用 {value} 作为 Oracle 软件所有者",
        "env_base_dir": "安装根目录: {value}",
        "db_name": "创建数据库名称: {value}",
        "db_characterset": "数据库字符集: {value}",
        "nation_characterset": "国家字符集: {value}",
        "db_block_size": "数据库块大小: {value} bytes",
        "pdbname": "创建 Pluggable Database: {value}",
        "redosize": "Redo 日志组大小: {value} MB",
        "enable_arch": "启用归档日志模式",
        "oradata_dir": "数据文件目录: {value}",
        "archive_dir": "归档日志目录: {value}",
        "data_asm_group": "数据 ASM 磁盘组: {value}",
        "arch_asm_group": "归档 ASM 磁盘组: {value}",
        "data_base_disk": "ASM 数据磁盘: {value}",
        "data_redun": "数据磁盘组冗余度: {value}",
        "local_ifname": "公网网卡: {value}",
        "grid_user": "使用 {value} 作为 Grid 软件所有者",
        "local_repo": "使用本地软件源",
        "huge_flag": "配置大页内存",
        "only_conf_os": "仅配置操作系统，不安装数据库",
        "install_until_db": "安装到 DB 软件完成",
        "install_until_grid": "安装到 Grid 软件完成",
        "optimize_db": "安装完成后执行数据库优化",
        "oracle_patch": "应用 Oracle PSU/RU 补丁: {value}",
        "ojvm_patch": "应用 OJVM PSU/RU 补丁: {value}",
        "grid_patch": "应用 Grid PSU/RU 补丁: {value}",
        "rac_priv_ifname": "RAC 心跳网卡: {value}",
        "cluster_name": "集群名称: {value}",
        "scan_name": "SCAN 名称: {value}",
        "rac_scan_ip": "SCAN IP: {value}",
        "multipath": "启用 Multipath 多路径",
        "asm_disk_conf": "脚本自动配置 ASM 磁盘",
    }

    for field, flag, default in FLAG_MAP:
        if mode == "single" and field in ASM_FIELDS:
            continue
        if mode == "single" and field in RAC_FIELDS:
            continue
        if mode == "standalone" and field in RAC_FIELDS:
            continue
        if field == "mode":
            continue

        val = data.get(field, "")
        val_str = str(val)
        if val_str and val_str != str(default):
            parts.append("{} {}".format(flag, val_str))
            tags.append("{} {}".format(flag, val_str))
            label = param_labels.get(field, "")
            if label:
                steps.append(label.replace("{value}", val_str))

    parts.append("-install_mode {}".format(mode))

    command = " \\\n    ".join(parts)
    return command, tags, steps


@router.post("/generate", response_model=InstallResponse)
def generate_install_command(
    body: InstallRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    command, tags, steps = _build_command(body)

    history = History(
        user_id=user.id,
        tool="installer",
        oracle_version=body.db_version or "unknown",
        connection="{}",
        params=body.model_dump_json(),
        command=command,
    )
    db.add(history)
    db.commit()

    return InstallResponse(command=command, params_summary=tags, steps=steps)


SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "static", "OracleShellInstall.sh")


@router.get("/download-script")
def download_script(_user=Depends(get_current_user)):
    path = os.path.normpath(SCRIPT_PATH)
    if not os.path.isfile(path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="脚本文件不存在")
    return FileResponse(path, filename="OracleShellInstall.sh", media_type="application/x-sh")
