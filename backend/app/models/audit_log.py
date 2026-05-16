from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    action = Column(String(50), nullable=False, index=True)  # login/generate/delete/test/create_env/...
    target = Column(String(100), default="")  # what was acted on
    detail = Column(Text, default="")
    ip_address = Column(String(45), default="")
    created_at = Column(DateTime, server_default=func.now())
