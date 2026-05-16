import os

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.optimizer import OptimizeRequest, OptimizeResponse, FLAG_MAP, ALL_STEPS
from app.models.history import History
from app.api.v1.auth import get_current_user

router = APIRouter()


def _build_command(req: OptimizeRequest) -> tuple[str, list[str]]:
    parts = ["./Oracle_19c_Optimize.sh"]
    tags = []
    is_asm = req.mode in ("rac", "standalone")
    data = req.model_dump()

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

    # Steps
    if req.steps and set(req.steps) != set(ALL_STEPS):
        parts.append("-s {}".format(",".join(req.steps)))
    if set(req.steps) == set(ALL_STEPS):
        tags.append("all steps")
    else:
        tags.extend(req.steps)

    if req.restart_after:
        parts.append("-z")
        tags.append("-z")

    command = " \\\n    ".join(parts)
    return command, tags


@router.post("/generate", response_model=OptimizeResponse)
def generate_optimizer_command(
    body: OptimizeRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    command, tags = _build_command(body)

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

    return OptimizeResponse(command=command, params_summary=tags)


SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "static", "Oracle_19c_Optimize.sh")


@router.get("/download-script")
def download_script(_user=Depends(get_current_user)):
    path = os.path.normpath(SCRIPT_PATH)
    if not os.path.isfile(path):
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="脚本文件不存在")
    return FileResponse(path, filename="Oracle_19c_Optimize.sh", media_type="application/x-sh")
