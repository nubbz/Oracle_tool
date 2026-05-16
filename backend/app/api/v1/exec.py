import threading
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.environment import Environment
from app.services import exec_service
from app.services.rbac_service import require_operator
from app.services.crypto_service import decrypt, is_encrypted

router = APIRouter()


class ExecRequest(BaseModel):
    env_id: int
    command: str


class ExecResponse(BaseModel):
    task_id: str
    status: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    output: str
    exit_code: int | None
    started_at: str
    finished_at: str


@router.post("", response_model=ExecResponse)
def execute_command(
    body: ExecRequest,
    db: Session = Depends(get_db),
    user=Depends(require_operator),
):
    env = db.query(Environment).filter(
        Environment.id == body.env_id,
        Environment.user_id == user.id,
    ).first()
    if not env:
        raise HTTPException(status_code=404, detail="环境不存在")
    if not env.ssh_enabled:
        raise HTTPException(status_code=400, detail="该环境未启用 SSH")

    # Decrypt passwords for execution
    if env.ssh_password and is_encrypted(env.ssh_password):
        env.ssh_password = decrypt(env.ssh_password)
    if env.ssh_key_passphrase and is_encrypted(env.ssh_key_passphrase):
        env.ssh_key_passphrase = decrypt(env.ssh_key_passphrase)

    task = exec_service.submit_task(user.id, body.env_id, body.command)

    # Run in background thread
    t = threading.Thread(target=exec_service.run_task, args=(task.id, env), daemon=True)
    t.start()

    return ExecResponse(task_id=task.id, status=task.status)


@router.get("/{task_id}", response_model=TaskStatusResponse)
def get_task_status(
    task_id: str,
    user=Depends(require_operator),
):
    task = exec_service.get_task(task_id)
    if not task or task.user_id != user.id:
        raise HTTPException(status_code=404, detail="任务不存在")
    return TaskStatusResponse(
        task_id=task.id, status=task.status, output=task.output,
        exit_code=task.exit_code, started_at=task.started_at, finished_at=task.finished_at,
    )


@router.get("", response_model=list[TaskStatusResponse])
def list_tasks(
    limit: int = 50,
    user=Depends(require_operator),
):
    tasks = exec_service.list_tasks(user.id, limit)
    return [
        TaskStatusResponse(
            task_id=t.id, status=t.status, output=t.output,
            exit_code=t.exit_code, started_at=t.started_at, finished_at=t.finished_at,
        ) for t in tasks
    ]
