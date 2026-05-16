import json as _json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.history import HistoryResponse
from app.services.history_service import HistoryService
from app.services import crypto_service
from app.api.v1.auth import get_current_user

router = APIRouter()
service = HistoryService()

SENSITIVE_FIELDS = ("password", "ssh_password", "ssh_key_passphrase", "encryption_password")


def _json_loads(s: str) -> dict:
    try:
        return _json.loads(s) if s else {}
    except Exception:
        return {}


def _mask_connection(conn: dict) -> dict:
    """Decrypt then mask sensitive fields for API response."""
    out = dict(conn)
    for field in SENSITIVE_FIELDS:
        if field in out and out[field]:
            out[field] = "***"
    return out


@router.get("", response_model=dict)
def list_history(
    tool: str = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    items, total = service.list(db, user.id, tool, page, page_size)
    return {
        "items": [
            HistoryResponse(
                id=h.id,
                tool=h.tool,
                oracle_version=h.oracle_version,
                connection=_mask_connection(_json_loads(h.connection)),
                params=_json_loads(h.params),
                command=h.command,
                created_at=h.created_at.isoformat() if h.created_at else "",
            )
            for h in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{history_id}", response_model=HistoryResponse)
def get_history(
    history_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    h = service.get(db, user.id, history_id)
    if not h:
        raise HTTPException(status_code=404, detail="记录不存在")
    return HistoryResponse(
        id=h.id, tool=h.tool, oracle_version=h.oracle_version,
        connection=_mask_connection(_json_loads(h.connection)), params=_json_loads(h.params),
        command=h.command,
        created_at=h.created_at.isoformat() if h.created_at else "",
    )


@router.delete("/{history_id}", status_code=204)
def delete_history(
    history_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if not service.delete(db, user.id, history_id):
        raise HTTPException(status_code=404, detail="记录不存在")


@router.delete("", status_code=204)
def clear_history(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    service.delete_all(db, user.id)
