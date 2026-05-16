import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.generator import GenerateRequest, GenerateResponse, ValidationWarning
from app.services.command_service import CommandService
from app.models.history import History
from app.api.v1.auth import get_current_user

router = APIRouter()
command_service = CommandService()


@router.post("/generate", response_model=GenerateResponse)
def generate(
    body: GenerateRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    try:
        result = command_service.generate(
            tool=body.tool,
            oracle_version=body.oracle_version,
            connection=body.connection.model_dump(),
            params=body.params,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # 保存历史记录
    history = History(
        user_id=user.id,
        tool=body.tool,
        oracle_version=body.oracle_version,
        connection=json.dumps(body.connection.model_dump(), ensure_ascii=False),
        params=json.dumps(body.params, ensure_ascii=False),
        command=result["command"],
    )
    db.add(history)
    db.commit()

    return GenerateResponse(
        command=result["command"],
        parfile=result["parfile"],
        script=result["script"],
        warnings=[ValidationWarning(**w) for w in result["warnings"]],
        recommendations=result["recommendations"],
        directory_ddl=result.get("directory_ddl", ""),
    )


@router.post("/generate/reverse", response_model=GenerateResponse)
def generate_reverse(
    body: GenerateRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if body.tool not in ("expdp", "exp"):
        raise HTTPException(status_code=400, detail="反向生成仅支持 expdp 和 exp 工具")

    try:
        result = command_service.reverse_generate(
            tool=body.tool,
            oracle_version=body.oracle_version,
            connection=body.connection.model_dump(),
            params=body.params,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # 保存历史记录
    reverse_tool = "impdp" if body.tool == "expdp" else "imp"
    history = History(
        user_id=user.id,
        tool=reverse_tool,
        oracle_version=body.oracle_version,
        connection=json.dumps(body.connection.model_dump(), ensure_ascii=False),
        params=json.dumps(body.params, ensure_ascii=False),
        command=result["command"],
    )
    db.add(history)
    db.commit()

    return GenerateResponse(
        command=result["command"],
        parfile=result["parfile"],
        script=result["script"],
        warnings=[ValidationWarning(**w) for w in result["warnings"]],
        recommendations=result["recommendations"],
        directory_ddl=result.get("directory_ddl", ""),
    )
