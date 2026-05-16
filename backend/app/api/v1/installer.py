import os

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.installer import InstallRequest, InstallResponse, FLAG_MAP, ASM_FIELDS, RAC_FIELDS
from app.models.history import History
from app.api.v1.auth import get_current_user

router = APIRouter()


def _build_command(req: InstallRequest) -> tuple[str, list[str]]:
    parts = ["./OracleShellInstall"]
    tags = []
    data = req.model_dump()
    mode = req.mode

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

    parts.append("-install_mode {}".format(mode))

    command = " \\\n    ".join(parts)
    return command, tags


@router.post("/generate", response_model=InstallResponse)
def generate_install_command(
    body: InstallRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    command, tags = _build_command(body)

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

    return InstallResponse(command=command, params_summary=tags)


SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "static", "OracleShellInstall.sh")


@router.get("/download-script")
def download_script(_user=Depends(get_current_user)):
    path = os.path.normpath(SCRIPT_PATH)
    if not os.path.isfile(path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="脚本文件不存在")
    return FileResponse(path, filename="OracleShellInstall.sh", media_type="application/x-sh")
