
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # 應用設置
    APP_NAME: str = "ChemPatent Pro"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # 服務器設置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_HOSTS: List[str] = ["*"]

    # 安全設置
    SECRET_KEY: str = "chempatent-pro-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 文件設置
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_FILE_TYPES: List[str] = [".pdf", ".png", ".jpg", ".jpeg"]
    UPLOAD_DIR: str = "/tmp/uploads"

    # 處理設置
    MAX_CONCURRENT_TASKS: int = 5
    TASK_TIMEOUT: int = 300  # 5分鐘

    # OCR設置
    TESSERACT_CONFIG: str = "--psm 6"
    OCR_LANGUAGES: str = "chi_sim+chi_tra+eng+jpn"

    # 化學分析設置
    MAX_MOLECULES_PER_REQUEST: int = 100
    SIMILARITY_THRESHOLD: float = 0.8

    # 日誌設置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "{time} | {level} | {message}"

    # 數據庫設置（可選）
    DATABASE_URL: str = None

    # Redis設置（可選）
    REDIS_URL: str = None

    class Config:
        env_file = ".env"
        case_sensitive = True

# 創建設置實例
settings = Settings()

# 確保上傳目錄存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
