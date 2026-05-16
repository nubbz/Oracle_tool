from pydantic import BaseModel


class EnvironmentCreate(BaseModel):
    name: str
    env_type: str = "production"
    host: str = "localhost"
    port: int = 1521
    service_name: str = ""
    sid: str = ""
    connect_type: str = "service"
    description: str = ""
    # SSH Tunnel
    ssh_enabled: bool = False
    ssh_host: str = ""
    ssh_port: int = 22
    ssh_username: str = ""
    ssh_auth_method: str = "password"
    ssh_password: str = ""
    ssh_key_path: str = ""
    ssh_key_passphrase: str = ""
    # Container
    container_mode: str = ""
    pdb_name: str = ""


class EnvironmentUpdate(BaseModel):
    name: str | None = None
    env_type: str | None = None
    host: str | None = None
    port: int | None = None
    service_name: str | None = None
    sid: str | None = None
    connect_type: str | None = None
    description: str | None = None
    # SSH Tunnel
    ssh_enabled: bool | None = None
    ssh_host: str | None = None
    ssh_port: int | None = None
    ssh_username: str | None = None
    ssh_auth_method: str | None = None
    ssh_password: str | None = None
    ssh_key_path: str | None = None
    ssh_key_passphrase: str | None = None
    # Container
    container_mode: str | None = None
    pdb_name: str | None = None


class EnvironmentResponse(BaseModel):
    id: int
    name: str
    env_type: str
    host: str
    port: int
    service_name: str
    sid: str
    connect_type: str
    description: str
    # SSH Tunnel
    ssh_enabled: bool
    ssh_host: str
    ssh_port: int
    ssh_username: str
    ssh_auth_method: str
    ssh_password: str
    ssh_key_path: str
    ssh_key_passphrase: str
    # Container
    container_mode: str
    pdb_name: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
