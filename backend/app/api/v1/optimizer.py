import os

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.optimizer import OptimizeRequest, OptimizeResponse, FLAG_MAP, ALL_STEPS
from app.models.history import History
from app.api.v1.auth import get_current_user

router = APIRouter()


def _build_command(req: OptimizeRequest) -> tuple[str, list[str], list[str]]:
    parts = ["./Oracle_19c_Optimize.sh"]
    tags = []
    steps = []
    is_asm = req.mode in ("rac", "standalone")
    data = req.model_dump()

    step_names = {
        "omf": "配置 OMF（Oracle Managed Files）和归档路径",
        "redolog": "调整在线重做日志组大小和数量",
        "backup": "生成 RMAN 备份配置脚本",
        "para": "优化核心初始化参数（processes、memory、cursors 等）",
        "sqlnet": "配置 sqlnet.ora 网络参数",
        "glogin": "配置 glogin.sql 登录脚本",
    }

    param_labels = {
        "db_name": "指定数据库实例名为 {value}",
        "mode": "安装模式: {value}",
        "oracle_user": "使用 {value} 用户执行优化",
        "oracle_home": "Oracle Home 路径: {value}",
        "grid_home": "Grid Home 路径: {value}",
        "redosize": "调整 Redo 日志大小为 {value} MB",
        "processes": "设置 processes 参数为 {value}",
        "open_cursors": "设置 open_cursors 参数为 {value}",
        "session_cached_cursors": "设置 session_cached_cursors 为 {value}",
        "parallel_max_servers": "设置 parallel_max_servers 为 {value}",
        "undo_retention": "设置 undo_retention 为 {value} 秒",
        "db_files": "设置 db_files 为 {value}",
        "db_memory": "配置数据库总内存为 {value}（SGA:PGA = 80:20 自动分配）",
        "sga_target": "设置 SGA_TARGET 为 {value}",
        "pga_target": "设置 PGA_AGGREGATE_TARGET 为 {value}",
        "data_asm_group": "使用 ASM 磁盘组 {value} 存放数据文件",
        "arch_asm_group": "使用 ASM 磁盘组 {value} 存放归档日志",
        "backup_dir": "备份目录: {value}",
        "oradata_dir": "数据文件目录: {value}",
    }

    for field, flag, default in FLAG_MAP:
        if not is_asm and field in ("data_asm_group", "arch_asm_group"):
            continue
        if is_asm and field == "oradata_dir":
            continue

        val = data.get(field, "")
        val_str = str(val)
        if val_str and val_str != str(default):
            parts.append("{} {}".format(flag, val_str))
            tags.append("{} {}".format(flag, val_str))
            if field in param_labels:
                steps.append(param_labels[field].replace("{value}", val_str))

    # Steps
    if req.steps and set(req.steps) != set(ALL_STEPS):
        parts.append("-s {}".format(",".join(req.steps)))
    if set(req.steps) == set(ALL_STEPS):
        tags.append("all steps")
    else:
        tags.extend(req.steps)

    active_steps = [step_names.get(s, s) for s in req.steps if s in step_names]
    if active_steps:
        steps.insert(0, "将执行以下优化步骤: " + "、".join(active_steps))

    if req.restart_after:
        parts.append("-z")
        tags.append("-z")
        steps.append("优化完成后自动重启数据库")

    command = " \\\n    ".join(parts)
    return command, tags, steps


@router.post("/generate", response_model=OptimizeResponse)
def generate_optimizer_command(
    body: OptimizeRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    command, tags, steps = _build_command(body)

    # Save to history
    history = History(
        user_id=user.id,
        tool="optimizer",
        oracle_version="19c",
        connection="{}",
        params=body.model_dump_json(),
        command=command,
    )
    db.add(history)
    db.commit()

    return OptimizeResponse(command=command, params_summary=tags, steps=steps)


SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "static", "Oracle_19c_Optimize.sh")


@router.get("/download-script")
def download_script(_user=Depends(get_current_user)):
    path = os.path.normpath(SCRIPT_PATH)
    if not os.path.isfile(path):
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="脚本文件不存在")
    return FileResponse(path, filename="Oracle_19c_Optimize.sh", media_type="application/x-sh")
