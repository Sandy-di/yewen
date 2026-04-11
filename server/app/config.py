"""配置管理 — 环境变量 + 默认值"""

import os
from pathlib import Path
from functools import lru_cache


class Settings:
    """应用配置，所有配置通过环境变量注入"""

    # 应用
    APP_NAME: str = "业问"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # 数据库
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./yewen.db",  # 开发默认 SQLite
    )

    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "yewen-secret-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = int(os.getenv("JWT_EXPIRE_HOURS", "168"))  # 7天

    # 微信小程序
    WX_APPID: str = os.getenv("WX_APPID", "")
    WX_SECRET: str = os.getenv("WX_SECRET", "")

    # CORS
    CORS_ORIGINS: list = ["*"]

    # 分页
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100


@lru_cache()
def get_settings() -> Settings:
    return Settings()
