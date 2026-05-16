from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.sqlldr import SqlldrRequest, SqlldrResponse
from app.generators.sqlldr_gen import SqlldrGenerator
from app.services.rbac_service import require_operator

router = APIRouter()
generator = SqlldrGenerator()


@router.post("/generate", response_model=SqlldrResponse)
def generate_sqlldr(
    body: SqlldrRequest,
    user=Depends(require_operator),
):
    result = generator.generate(body.model_dump())
    if any(w["level"] == "error" for w in result["warnings"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["warnings"],
        )
    return SqlldrResponse(**result)
