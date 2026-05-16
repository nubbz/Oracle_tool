from fastapi import Depends, HTTPException, status
from app.api.v1.auth import get_current_user


def require_admin(user=Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限")
    return user


def require_operator(user=Depends(get_current_user)):
    if user.role not in ("admin", "operator"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要操作员权限")
    return user
