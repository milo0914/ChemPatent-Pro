FROM python:3.11-slim

# 設置工作目錄
WORKDIR /app

# 安裝系統依賴，一次完成、避免緩存殘留
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    tesseract-ocr \
    tesseract-ocr-chi-sim \
    tesseract-ocr-chi-tra \
    tesseract-ocr-jpn \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 複製需求文件、安裝 Python 依賴
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# 下載 spaCy 多國模型（單一 RUN，減少中斷）
RUN python -m spacy download en_core_web_sm && \
    python -m spacy download zh_core_web_sm && \
    python -m spacy download ja_core_news_sm

# 複製應用代碼
COPY . .

# 設置環境變量
ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 8000

# 健康檢查，URL 方括號請去掉
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# 優化 uvicorn 啟動（worker=1，timeout 減少時可先這樣，若非必要可調大）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]


# 啟動命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
