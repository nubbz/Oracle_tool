import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.template import TemplateCreate, TemplateUpdate, TemplateResponse
from app.models.template import Template
from app.api.v1.auth import get_current_user

router = APIRouter()


def _to_response(t: Template) -> TemplateResponse:
    params = {}
    try:
        params = json.loads(t.params) if t.params else {}
    except Exception:
        pass
    return TemplateResponse(
        id=t.id, name=t.name, description=t.description or "",
        tool=t.tool, oracle_version=t.oracle_version,
        params=params, is_builtin=bool(t.is_builtin),
        created_at=t.created_at.isoformat() if t.created_at else "",
        updated_at=t.updated_at.isoformat() if t.updated_at else "",
    )


@router.get("", response_model=list[TemplateResponse])
def list_templates(
    tool: str = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    q = db.query(Template).filter(
        (Template.user_id == user.id) | (Template.is_builtin == True)
    )
    if tool:
        q = q.filter(Template.tool == tool)
    items = q.order_by(Template.is_builtin.desc(), Template.updated_at.desc()).all()
    return [_to_response(t) for t in items]


@router.get("/{template_id}", response_model=TemplateResponse)
def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    t = db.query(Template).filter(
        Template.id == template_id,
        (Template.user_id == user.id) | (Template.is_builtin == True),
    ).first()
    if not t:
        raise HTTPException(status_code=404, detail="模板不存在")
    return _to_response(t)


@router.post("", response_model=TemplateResponse, status_code=201)
def create_template(
    body: TemplateCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    t = Template(
        user_id=user.id,
        name=body.name,
        description=body.description,
        tool=body.tool,
        oracle_version=body.oracle_version,
        params=json.dumps(body.params, ensure_ascii=False),
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return _to_response(t)


@router.put("/{template_id}", response_model=TemplateResponse)
def update_template(
    template_id: int,
    body: TemplateUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    t = db.query(Template).filter(Template.id == template_id, Template.user_id == user.id).first()
    if not t:
        raise HTTPException(status_code=404, detail="模板不存在")
    if t.is_builtin:
        raise HTTPException(status_code=403, detail="内置模板不可修改")
    data = body.model_dump(exclude_none=True)
    if "params" in data:
        data["params"] = json.dumps(data["params"], ensure_ascii=False)
    for key, val in data.items():
        setattr(t, key, val)
    db.commit()
    db.refresh(t)
    return _to_response(t)


@router.delete("/{template_id}", status_code=204)
def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    t = db.query(Template).filter(Template.id == template_id, Template.user_id == user.id).first()
    if not t:
        raise HTTPException(status_code=404, detail="模板不存在")
    if t.is_builtin:
        raise HTTPException(status_code=403, detail="内置模板不可删除")
    db.delete(t)
    db.commit()


@router.post("/seed", status_code=201)
def seed_builtin_templates(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Seed built-in DBA templates (idempotent)."""
    existing = db.query(Template).filter(Template.is_builtin == True).count()
    if existing > 0:
        return {"message": f"已有 {existing} 个内置模板"}

    seeds = [
        {
            "name": "每日全库 Schema 导出",
            "description": "适用于每日定时备份，包含压缩和并行设置",
            "tool": "expdp",
            "oracle_version": "19c",
            "params": {
                "directory": "DP_DIR",
                "dumpfile": "schema_backup_%U.dmp",
                "logfile": "schema_backup.log",
                "schemas": "",
                "parallel": 4,
                "compression": "ALL",
                "reuse_dumpfiles": True,
                "flashback_time": "SYSTIMESTAMP",
            },
        },
        {
            "name": "快速表空间迁移",
            "description": "用于表空间迁移，包含 REMAP 和 PARALLEL",
            "tool": "impdp",
            "oracle_version": "19c",
            "params": {
                "directory": "DP_DIR",
                "dumpfile": "ts_backup_%U.dmp",
                "logfile": "ts_import.log",
                "table_exists_action": "REPLACE",
                "parallel": 4,
                "transform": "SEGMENT_ATTRIBUTES:N",
            },
        },
        {
            "name": "RMAN 全库备份 + 压缩",
            "description": "基础全库备份脚本，BASIC 压缩，双通道",
            "tool": "rman",
            "oracle_version": "19c",
            "params": {
                "backup_type": "full",
                "scope": "database",
                "channel_count": 2,
                "compression": "BASIC",
                "format_path": "/backup/rman",
                "retention_policy": "REDUNDANCY 3",
            },
        },
        {
            "name": "RMAN 增量备份 Level 1",
            "description": "日常增量备份，配合 Level 0 基线使用",
            "tool": "rman",
            "oracle_version": "19c",
            "params": {
                "backup_type": "incremental",
                "incremental_level": 1,
                "scope": "database",
                "channel_count": 2,
                "compression": "BASIC",
                "format_path": "/backup/rman/incr",
            },
        },
        {
            "name": "传统 exp 逻辑备份",
            "description": "适用于 Oracle 10g/11g 旧版本兼容导出",
            "tool": "exp",
            "oracle_version": "11g",
            "params": {
                "file": "exp_backup.dmp",
                "logfile": "exp_backup.log",
                "direct": True,
                "consistent": True,
                "buffer": 10485760,
                "statistics": "NONE",
            },
        },
    ]

    for seed in seeds:
        t = Template(
            user_id=user.id,
            name=seed["name"],
            description=seed["description"],
            tool=seed["tool"],
            oracle_version=seed["oracle_version"],
            params=json.dumps(seed["params"], ensure_ascii=False),
            is_builtin=True,
        )
        db.add(t)
    db.commit()
    return {"message": f"已创建 {len(seeds)} 个内置模板"}
