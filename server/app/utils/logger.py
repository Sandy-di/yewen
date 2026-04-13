"""统一日志配置"""

import logging
import sys
from app.config import get_settings


def setup_logging() -> None:
    """配置应用日志"""
    settings = get_settings()
    level = logging.DEBUG if settings.DEBUG else logging.INFO

    # 根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # 格式
    fmt = logging.Formatter(
        "[%(asctime)s] %(levelname)-7s %(name)-20s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(fmt)

    # 避免重复添加
    if not root_logger.handlers:
        root_logger.addHandler(console_handler)

    # 第三方库日志级别
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DEBUG else logging.WARNING
    )


def get_logger(name: str) -> logging.Logger:
    """获取命名日志器"""
    return logging.getLogger(f"yewen.{name}")
