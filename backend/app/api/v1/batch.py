from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.command_service import CommandService
from app.services.rbac_service import require_operator
from app.models.history import History
from app.api.v1.generate import _encrypt_connection
import json

router = APIRouter()
command_service = CommandService()


class BatchGenerateRequest(BaseModel):
    tool: str  # expdp/exp/impdp/imp
    oracle_version: str = "19c"
    # Shared connection template
    connection: dict
    # List of param overrides (one per command)
    params_list: list[dict]


class BatchGenerateResponse(BaseModel):
    results: list[dict]
    total: int
    errors: int


@router.post("/generate", response_model=BatchGenerateResponse)
def batch_generate(
    body: BatchGenerateRequest,
    db: Session = Depends(get_db),
    user=Depends(require_operator),
):
    if body.tool not in ("expdp", "exp", "impdp", "imp"):
        raise HTTPException(status_code=400, detail="不支持的工具类型")

    results = []
    errors = 0

    for i, params in enumerate(body.params_list):
        try:
            result = command_service.generate(
                tool=body.tool,
                oracle_version=body.oracle_version,
                connection=body.connection,
                params=params,
            )
            # Save to history
            from app.schemas.generator import ConnectionParams
            safe_conn = _encrypt_connection(body.connection)
            history = History(
                user_id=user.id,
                tool=body.tool,
                oracle_version=body.oracle_version,
                connection=json.dumps(safe_conn, ensure_ascii=False),
                params=json.dumps(params, ensure_ascii=False),
                command=result["command"],
            )
            db.add(history)

            results.append({
                "index": i,
                "command": result["command"],
                "parfile": result["parfile"],
                "script": result["script"],
                "warnings": result["warnings"],
            })
        except Exception as ex:
            results.append({"index": i, "error": str(ex)})
            errors += 1

    db.commit()

    return BatchGenerateResponse(results=results, total=len(body.params_list), errors=errors)
