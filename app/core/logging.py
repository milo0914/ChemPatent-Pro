
import sys
from loguru import logger
from app.core.config import settings

def setup_logging():
    """設置日誌配置"""
    # 清除默認處理器
    logger.remove()

    # 添加控制台處理器
    logger.add(
        sys.stdout,
        format=settings.LOG_FORMAT,
        level=settings.LOG_LEVEL,
        colorize=True
    )

    # 添加文件處理器（如果在生產環境）
    if not settings.DEBUG:
        logger.add(
            "logs/app.log",
            format=settings.LOG_FORMAT,
            level=settings.LOG_LEVEL,
            rotation="1 day",
            retention="30 days",
            compression="zip"
        )

    logger.info(f"日誌系統已初始化，級別: {settings.LOG_LEVEL}")
