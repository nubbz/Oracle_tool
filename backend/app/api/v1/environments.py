from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.environment import EnvironmentCreate, EnvironmentUpdate, EnvironmentResponse
from app.models.environment import Environment
from app.api.v1.auth import get_current_user

router = APIRouter()


class OracleTestRequest(BaseModel):
    username: str = ""
    password: str = ""


def _to_response(e: Environment) -> dict:
    from app.services.crypto_service import decrypt, is_encrypted

    ssh_pwd = e.ssh_password or ""
    ssh_passphrase = e.ssh_key_passphrase or ""

    if ssh_pwd and is_encrypted(ssh_pwd):
        ssh_pwd = decrypt(ssh_pwd)
    if ssh_passphrase and is_encrypted(ssh_passphrase):
        ssh_passphrase = decrypt(ssh_passphrase)

    return EnvironmentResponse(
        id=e.id, name=e.name, env_type=e.env_type,
        host=e.host, port=e.port, service_name=e.service_name,
        sid=e.sid, connect_type=e.connect_type, description=e.description,
        ssh_enabled=bool(e.ssh_enabled),
        ssh_host=e.ssh_host or "",
        ssh_port=e.ssh_port or 22,
        ssh_username=e.ssh_username or "",
        ssh_auth_method=e.ssh_auth_method or "password",
        ssh_password="***" if ssh_pwd else "",
        ssh_key_path=e.ssh_key_path or "",
        ssh_key_passphrase="***" if ssh_passphrase else "",
        container_mode=e.container_mode or "",
        pdb_name=e.pdb_name or "",
        created_at=e.created_at.isoformat() if e.created_at else "",
        updated_at=e.updated_at.isoformat() if e.updated_at else "",
    ).model_dump()


@router.get("", response_model=list[EnvironmentResponse])
def list_environments(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    items = db.query(Environment).filter(Environment.user_id == user.id).order_by(Environment.updated_at.desc()).all()
    return [_to_response(e) for e in items]


@router.get("/{env_id}", response_model=EnvironmentResponse)
def get_environment(
    env_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    e = db.query(Environment).filter(Environment.id == env_id, Environment.user_id == user.id).first()
    if not e:
        raise HTTPException(status_code=404, detail="环境不存在")
    return _to_response(e)


@router.post("", response_model=EnvironmentResponse, status_code=201)
def create_environment(
    body: EnvironmentCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    from app.services.crypto_service import encrypt
    data = body.model_dump()
    data["ssh_enabled"] = 1 if data.get("ssh_enabled") else 0
    if data.get("ssh_password"):
        data["ssh_password"] = encrypt(data["ssh_password"])
    if data.get("ssh_key_passphrase"):
        data["ssh_key_passphrase"] = encrypt(data["ssh_key_passphrase"])
    e = Environment(user_id=user.id, **data)
    db.add(e)
    db.commit()
    db.refresh(e)
    return _to_response(e)


@router.put("/{env_id}", response_model=EnvironmentResponse)
def update_environment(
    env_id: int,
    body: EnvironmentUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    from app.services.crypto_service import encrypt
    e = db.query(Environment).filter(Environment.id == env_id, Environment.user_id == user.id).first()
    if not e:
        raise HTTPException(status_code=404, detail="环境不存在")
    update_data = body.model_dump(exclude_none=True)
    if update_data.get("ssh_password") == "***":
        del update_data["ssh_password"]
    elif update_data.get("ssh_password"):
        update_data["ssh_password"] = encrypt(update_data["ssh_password"])
    if update_data.get("ssh_key_passphrase") == "***":
        del update_data["ssh_key_passphrase"]
    elif update_data.get("ssh_key_passphrase"):
        update_data["ssh_key_passphrase"] = encrypt(update_data["ssh_key_passphrase"])
    if "ssh_enabled" in update_data:
        update_data["ssh_enabled"] = 1 if update_data["ssh_enabled"] else 0
    for key, val in update_data.items():
        setattr(e, key, val)
    db.commit()
    db.refresh(e)
    return _to_response(e)


@router.delete("/{env_id}", status_code=204)
def delete_environment(
    env_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    e = db.query(Environment).filter(Environment.id == env_id, Environment.user_id == user.id).first()
    if not e:
        raise HTTPException(status_code=404, detail="环境不存在")
    db.delete(e)
    db.commit()


@router.post("/{env_id}/test-ssh")
def test_ssh_connection(
    env_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    from app.services.crypto_service import decrypt, is_encrypted
    e = db.query(Environment).filter(Environment.id == env_id, Environment.user_id == user.id).first()
    if not e:
        raise HTTPException(status_code=404, detail="环境不存在")
    if not e.ssh_enabled:
        raise HTTPException(status_code=400, detail="该环境未启用 SSH 隧道")
    if e.ssh_password and is_encrypted(e.ssh_password):
        e.ssh_password = decrypt(e.ssh_password)
    if e.ssh_key_passphrase and is_encrypted(e.ssh_key_passphrase):
        e.ssh_key_passphrase = decrypt(e.ssh_key_passphrase)
    try:
        from app.services.ssh_service import test_ssh
        return test_ssh(e)
    except ImportError:
        return {"success": False, "error": "paramiko 未安装，请运行 pip install paramiko", "connection_time": 0}


@router.post("/{env_id}/test-oracle")
def test_oracle_connection(
    env_id: int,
    body: OracleTestRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    e = db.query(Environment).filter(Environment.id == env_id, Environment.user_id == user.id).first()
    if not e:
        raise HTTPException(status_code=404, detail="环境不存在")
    if not body.username or not body.password:
        raise HTTPException(status_code=400, detail="请提供数据库用户名和密码")
    try:
        from app.services.oracle_service import test_oracle
        return test_oracle(
            host=e.host, port=e.port,
            service_name=e.service_name, sid=e.sid,
            connect_type=e.connect_type,
            username=body.username, password=body.password,
        )
    except ImportError:
        return {"success": False, "error": "oracledb 未安装，请运行 pip install oracledb",
                "response_time": 0, "instance_name": "", "status": "", "version": ""}
