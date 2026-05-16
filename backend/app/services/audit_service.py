from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog


def log_action(db: Session, user_id: int, action: str, target: str = "", detail: str = "", ip_address: str = ""):
    entry = AuditLog(
        user_id=user_id,
        action=action,
        target=target,
        detail=detail,
        ip_address=ip_address,
    )
    db.add(entry)
    db.commit()
