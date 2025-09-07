#!/bin/bash

# ChemPatent Pro Railway 快速部署指令
# 執行此腳本前，請確保已安裝 Railway CLI

echo "🚀 ChemPatent Pro Railway 快速部署"
echo "================================="

# 檢查Railway CLI
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI 未安裝"
    echo "請先安裝: npm install -g @railway/cli"
    exit 1
fi

echo "✅ Railway CLI 已安裝"

# 步驟1: 登入Railway
echo "\n🔐 步驟1: 登入Railway"
echo "執行: railway login"
railway login

# 步驟2: 初始化項目
echo "\n📁 步驟2: 初始化Railway項目"
echo "執行: railway init"
railway init

# 步驟3: 設置環境變量
echo "\n⚙️ 步驟3: 設置環境變量"
railway variables set PYTHONPATH=/app
railway variables set PYTHONDONTWRITEBYTECODE=1
railway variables set PYTHONUNBUFFERED=1

echo "✅ 環境變量設置完成"

# 步驟4: 部署應用
echo "\n🚀 步驟4: 部署應用"
echo "執行: railway up"
railway up

# 步驟5: 生成域名
echo "\n🌐 步驟5: 生成域名"
echo "執行: railway domain"
railway domain

# 完成
echo "\n🎉 部署完成！"
echo "查看日誌: railway logs"
echo "查看狀態: railway status"
echo "訪問應用: railway open"

# 顯示有用的命令
echo "\n📋 有用的Railway命令:"
echo "  railway logs          - 查看應用日誌"
echo "  railway logs --follow - 實時監控日誌"
echo "  railway status        - 查看服務狀態"
echo "  railway open          - 在瀏覽器中打開應用"
echo "  railway redeploy      - 重新部署"
echo "  railway variables     - 查看環境變量"
