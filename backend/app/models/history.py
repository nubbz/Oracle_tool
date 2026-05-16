from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from app.database import Base


class History(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    tool = Column(String(10), nullable=False)
    oracle_version = Column(String(10), default="19c")
    connection = Column(Text, default="{}")
    params = Column(Text, default="{}")
    command = Column(Text, default="")
    created_at = Column(DateTime, server_default=func.now())
