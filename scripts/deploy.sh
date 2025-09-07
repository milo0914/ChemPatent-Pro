#!/bin/bash

# Railway 部署腳本
echo "🚀 開始 Railway 部署流程..."

# 設置環境變量
export PYTHONPATH=/app
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1

# 創建必要目錄
mkdir -p /tmp/uploads
mkdir -p logs

# 安裝 Python 依賴
echo "📦 安裝 Python 依賴..."
pip install --no-cache-dir -r requirements.txt

# 下載 spaCy 模型
echo "📚 下載 spaCy 語言模型..."
python -m spacy download en_core_web_sm || echo "⚠️  English model download failed"
python -m spacy download zh_core_web_sm || echo "⚠️  Chinese model download failed"  
python -m spacy download ja_core_news_sm || echo "⚠️  Japanese model download failed"

# 檢查必要的系統命令
echo "🔍 檢查系統依賴..."
which tesseract || echo "⚠️  Tesseract not found"
which convert || echo "⚠️  ImageMagick not found"

echo "✅ 部署準備完成！"
echo "🌟 啟動 ChemPatent Pro..."

# 啟動應用
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1
