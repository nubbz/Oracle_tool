from datetime import datetime
import traceback

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import engine, Base, migrate_environment_ssh_columns, migrate_environment_container_columns, migrate_encrypt_passwords, migrate_user_role
from app.models.template import Template  # noqa: F401 — ensure table creation
from app.models.audit_log import AuditLog  # noqa: F401 — ensure table creation
from app.api.v1 import auth, generate, history, environments, optimizer, installer, rman, templates, audit, exec, batch, sqlldr

Base.metadata.create_all(bind=engine)
migrate_environment_ssh_columns()
migrate_environment_container_columns()
migrate_encrypt_passwords()
migrate_user_role()

app = FastAPI(
    title="Oracle Backup Command Generator",
    description="商业级 Oracle 数据库备份/导入命令生成工具 API",
    version="1.0.0",
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    traceback.print_exc()
    return JSONResponse(status_code=500, content={"detail": str(exc)})

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(generate.router, prefix="/api/v1", tags=["命令生成"])
app.include_router(history.router, prefix="/api/v1/history", tags=["历史记录"])
app.include_router(environments.router, prefix="/api/v1/environments", tags=["环境管理"])
app.include_router(optimizer.router, prefix="/api/v1/optimizer", tags=["DB优化"])
app.include_router(installer.router, prefix="/api/v1/installer", tags=["DB安装"])
app.include_router(rman.router, prefix="/api/v1/rman", tags=["RMAN"])
app.include_router(templates.router, prefix="/api/v1/templates", tags=["模板"])
app.include_router(audit.router, prefix="/api/v1/audit", tags=["审计日志"])
app.include_router(exec.router, prefix="/api/v1/exec", tags=["远程执行"])
app.include_router(batch.router, prefix="/api/v1/batch", tags=["批量生成"])
app.include_router(sqlldr.router, prefix="/api/v1/sqlldr", tags=["SQL*Loader"])


@app.get("/api/v1/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}
