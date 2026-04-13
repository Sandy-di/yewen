"""FastAPI 入口 — 应用创建、中间件注册、路由挂载"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.config import get_settings
from app.database import init_db
from app.utils.logger import setup_logging, get_logger
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.middleware.rate_limit import limiter, rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化数据库"""
    setup_logging()
    logger.info(f"业问 API v{get_settings().APP_VERSION} 启动中...")
    await init_db()

    # 确保上传目录存在
    upload_dir = Path(get_settings().UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    logger.info("业问 API 启动完成")
    yield
    logger.info("业问 API 正在关闭...")


app = FastAPI(
    title="业问 API",
    description="智慧社区业主微信小程序后端服务",
    version="1.0.0",
    lifespan=lifespan,
)

# 限流
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# 全局异常处理
app.add_middleware(ErrorHandlerMiddleware)

# CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件 — 上传文件访问 + 管理后台
upload_dir = Path(settings.UPLOAD_DIR)
upload_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(upload_dir)), name="uploads")

# 管理后台静态页面
static_dir = Path(__file__).parent.parent / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/admin", StaticFiles(directory=str(static_dir), html=True), name="admin")

# 注册路由
from app.routers import auth, users, votes, orders, finance, announcements  # noqa: E402
from app.routers import community, upload, stats, complaints, vote_templates, notifications, meetings, archives  # noqa: E402

app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/users", tags=["用户"])
app.include_router(votes.router, prefix="/api/votes", tags=["投票"])
app.include_router(orders.router, prefix="/api/orders", tags=["报修工单"])
app.include_router(finance.router, prefix="/api/finance", tags=["财务公示"])
app.include_router(announcements.router, prefix="/api/announcements", tags=["公告通知"])
app.include_router(community.router, prefix="/api/communities", tags=["社区管理"])
app.include_router(upload.router, prefix="/api/upload", tags=["文件上传"])
app.include_router(stats.router, prefix="/api/stats", tags=["数据统计"])
app.include_router(complaints.router, prefix="/api/complaints", tags=["投诉建议"])
app.include_router(vote_templates.router, prefix="/api/vote-templates", tags=["投票模板"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["消息通知"])
app.include_router(meetings.router, prefix="/api/meetings", tags=["会议管理"])
app.include_router(archives.router, prefix="/api/archives", tags=["档案管理"])


@app.get("/api/health", tags=["系统"])
async def health_check():
    """健康检查"""
    from sqlalchemy import text
    from app.database import engine
    db_status = "ok"
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {e}"

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": db_status,
    }
