"""FastAPI 入口 — 应用创建、中间件注册、路由挂载"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化数据库"""
    await init_db()
    yield


app = FastAPI(
    title="业问 API",
    description="智慧社区业主微信小程序后端服务",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — 允许小程序请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
from app.routers import auth, users, votes, orders, finance, announcements  # noqa: E402

app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/users", tags=["用户"])
app.include_router(votes.router, prefix="/api/votes", tags=["投票"])
app.include_router(orders.router, prefix="/api/orders", tags=["报修工单"])
app.include_router(finance.router, prefix="/api/finance", tags=["财务公示"])
app.include_router(announcements.router, prefix="/api/announcements", tags=["公告通知"])


@app.get("/api/health", tags=["系统"])
async def health_check():
    return {"status": "ok", "app": "业问", "version": "1.0.0"}
