from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.audit_log import AuditLog
from app.api.v1.auth import get_current_user
from app.services.rbac_service import require_admin

router = APIRouter()


class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    action: str
    target: str
    detail: str
    ip_address: str
    created_at: str

    class Config:
        from_attributes = True


@router.get("", response_model=dict)
def list_audit_logs(
    action: str = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    q = db.query(AuditLog).order_by(AuditLog.created_at.desc())
    if action:
        q = q.filter(AuditLog.action == action)
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return {
        "items": [
            AuditLogResponse(
                id=a.id, user_id=a.user_id, action=a.action,
                target=a.target or "", detail=a.detail or "",
                ip_address=a.ip_address or "",
                created_at=a.created_at.isoformat() if a.created_at else "",
            ) for a in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }
