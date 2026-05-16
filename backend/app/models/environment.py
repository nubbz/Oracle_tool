from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from app.database import Base


class Environment(Base):
    __tablename__ = "environments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    env_type = Column(String(20), default="production")  # dev/test/uat/production
    host = Column(String(255), default="localhost")
    port = Column(Integer, default=1521)
    service_name = Column(String(255), default="")
    sid = Column(String(255), default="")
    connect_type = Column(String(10), default="service")
    description = Column(Text, default="")
    # SSH Tunnel
    ssh_enabled = Column(Integer, default=0)
    ssh_host = Column(String(255), default="")
    ssh_port = Column(Integer, default=22)
    ssh_username = Column(String(100), default="")
    ssh_auth_method = Column(String(10), default="password")
    ssh_password = Column(String(255), default="")
    ssh_key_path = Column(String(500), default="")
    ssh_key_passphrase = Column(String(255), default="")
    # Container Database
    container_mode = Column(String(10), default="")
    pdb_name = Column(String(100), default="")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
