from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, func
from app.database import Base


class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, default="")
    tool = Column(String(20), nullable=False)  # expdp/exp/impdp/imp/rman/optimizer/installer
    oracle_version = Column(String(10), default="19c")
    params = Column(Text, default="{}")  # JSON
    is_builtin = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
