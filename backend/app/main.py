from datetime import datetime
import traceback

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import engine, Base, migrate_environment_ssh_columns, migrate_environment_container_columns, migrate_encrypt_passwords
from app.api.v1 import auth, generate, history, environments, optimizer, installer

Base.metadata.create_all(bind=engine)
migrate_environment_ssh_columns()
migrate_environment_container_columns()
migrate_encrypt_passwords()

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


@app.get("/api/v1/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}
