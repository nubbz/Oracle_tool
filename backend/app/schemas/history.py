from pydantic import BaseModel


class HistoryResponse(BaseModel):
    id: int
    tool: str
    oracle_version: str
    connection: dict
    params: dict
    command: str
    created_at: str

    class Config:
        from_attributes = True
