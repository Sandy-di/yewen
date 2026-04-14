"""配置管理 — pydantic-settings + 环境变量校验"""

import os
import warnings
from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """应用配置，所有配置通过环境变量或 .env 文件注入"""

    # 应用
    APP_NAME: str = "业问"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 数据库
    DATABASE_URL: str = "sqlite+aiosqlite:///./yewen.db"

    # JWT
    JWT_SECRET: str = Field(
        default="yewen-secret-change-in-production",
        description="JWT签名密钥，生产环境必须通过环境变量设置",
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 168  # 7天

    # 微信小程序
    WX_APPID: str = ""
    WX_SECRET: str = ""

    # CORS
    CORS_ORIGINS: str = "*"  # 逗号分隔的域名列表，或 *

    # 分页
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # 文件上传
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    # 测试模式（开启后允许 dev-token 和身份切换接口）
    TEST_MODE: bool = False

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    @property
    def cors_origins_list(self) -> list[str]:
        """解析 CORS_ORIGINS 为列表"""
        if self.CORS_ORIGINS.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    def check_security(self) -> None:
        """启动时安全检查"""
        if self.JWT_SECRET == "yewen-secret-change-in-production":
            if not self.DEBUG:
                warnings.warn(
                    "⚠️  JWT_SECRET 使用默认值且非DEBUG模式，强烈建议设置强密钥！",
                    stacklevel=2,
                )
            else:
                warnings.warn(
                    "⚠️  JWT_SECRET 使用默认值，请勿在生产环境运行！",
                    stacklevel=2,
                )


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    settings.check_security()
    return settings
