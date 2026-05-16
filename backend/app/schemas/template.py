from pydantic import BaseModel
from typing import Optional


class TemplateCreate(BaseModel):
    name: str
    description: str = ""
    tool: str
    oracle_version: str = "19c"
    params: dict = {}


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tool: Optional[str] = None
    oracle_version: Optional[str] = None
    params: Optional[dict] = None


class TemplateResponse(BaseModel):
    id: int
    name: str
    description: str
    tool: str
    oracle_version: str
    params: dict
    is_builtin: bool
    created_at: str
    updated_at: str
