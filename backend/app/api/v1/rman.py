from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.rman import (
    RmanBackupRequest, RmanRestoreRequest, RmanConfigRequest, RmanResponse,
)
from app.generators.rman_gen import RmanGenerator
from app.api.v1.auth import get_current_user

router = APIRouter()
generator = RmanGenerator()


@router.post("/backup", response_model=RmanResponse)
def generate_rman_backup(
    body: RmanBackupRequest,
    user=Depends(get_current_user),
):
    result = generator.generate_backup(body.model_dump())
    if any(w["level"] == "error" for w in result["warnings"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["warnings"],
        )
    return RmanResponse(**result)


@router.post("/restore", response_model=RmanResponse)
def generate_rman_restore(
    body: RmanRestoreRequest,
    user=Depends(get_current_user),
):
    result = generator.generate_restore(body.model_dump())
    return RmanResponse(**result)


@router.post("/config", response_model=RmanResponse)
def generate_rman_config(
    body: RmanConfigRequest,
    user=Depends(get_current_user),
):
    result = generator.generate_config(body.model_dump())
    return RmanResponse(**result)
