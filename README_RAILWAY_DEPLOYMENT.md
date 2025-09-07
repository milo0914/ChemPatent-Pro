# ChemPatent Pro - Railway部署指南

## 🚀 項目概述

ChemPatent Pro 是一個先進的化學專利分析系統，集成了多語言PDF解析、化學結構識別、專利權利要求分析和分子性質計算等功能。

### 核心功能
- 📄 **多語言PDF解析**: 支援中文、英文、日文的PDF文件解析和OCR
- 🧪 **化學結構識別**: SMILES轉換、分子指紋生成、官能基檢測
- 📊 **專利權利要求分析**: 權利要求提取、依賴關係分析、創新性檢測
- 🔬 **分子性質計算**: Lipinski規則、QED評分、ADMET預測
- 🌐 **響應式前端**: Bootstrap界面，支援多種分析工具
- ⚡ **FastAPI後端**: 高性能異步API，完整的錯誤處理

### 技術架構
- **後端**: FastAPI + Python 3.11
- **前端**: Bootstrap + JavaScript (ES6+)
- **化學計算**: RDKit + OpenCV
- **NLP處理**: spaCy (多語言模型)
- **容器化**: Docker + Railway部署
- **數據處理**: pandas + numpy + scipy

## 📦 系統文件

### AI Drive位置
```
/deployments/chempatent-pro-20250905_151631.tar.gz (40KB)
```

### 項目結構
```
chempatent-pro/
├── app/                          # 核心應用
│   ├── api/                      # API路由
│   ├── core/                     # 核心配置
│   ├── models/                   # 數據模型
│   ├── services/                 # 業務邏輯
│   └── main.py                   # 應用入口
├── frontend/                     # 前端文件
│   ├── templates/               # HTML模板
│   └── static/                  # 靜態資源
├── tests/                       # 測試文件
├── scripts/                     # 部署腳本
├── requirements.txt             # Python依賴
├── Dockerfile                   # Docker配置
├── railway.json                 # Railway配置
└── docker-compose.yml          # 本地開發配置
```

## 🛠️ Railway部署步驟

### 步驟1: 準備項目
```bash
# 1. 下載項目壓縮文件
wget https://your-aidrive-url/deployments/chempatent-pro-20250905_151631.tar.gz

# 2. 解壓縮項目
tar -xzf chempatent-pro-20250905_151631.tar.gz
cd chempatent-pro

# 3. 檢查項目完整性
python scripts/check_config.py
```

### 步驟2: 建立Git倉庫
```bash
# 初始化Git倉庫
git init
git add .
git commit -m "Initial commit: ChemPatent Pro v1.0"

# 連接到GitHub (可選)
git remote add origin https://github.com/yourusername/chempatent-pro.git
git push -u origin main
```

### 步驟3: Railway部署

#### 方法A: 從GitHub部署 (推薦)
```bash
# 1. 登入Railway
railway login

# 2. 創建新項目
railway new

# 3. 連接GitHub倉庫
railway add

# 4. 部署項目
railway up
```

#### 方法B: 直接部署
```bash
# 1. 登入Railway
railway login

# 2. 初始化Railway項目
railway init

# 3. 部署應用
railway up

# 4. 生成域名
railway domain
```

### 步驟4: 配置環境變量 (可選)
```bash
# 設置環境變量
railway variables set PYTHONPATH=/app
railway variables set PYTHONDONTWRITEBYTECODE=1
railway variables set PYTHONUNBUFFERED=1

# 設置自定義配置 (如果需要)
railway variables set LOG_LEVEL=info
railway variables set MAX_UPLOAD_SIZE=50
```

### 步驟5: 監控部署
```bash
# 查看部署日誌
railway logs

# 查看服務狀態
railway status

# 查看域名
railway domain
```

## 🔧 本地開發設置

### 使用Docker Compose
```bash
# 1. 構建和啟動服務
docker-compose up --build

# 2. 訪問應用
open http://localhost:8000

# 3. 停止服務
docker-compose down
```

### 直接Python運行
```bash
# 1. 安裝依賴
pip install -r requirements.txt

# 2. 下載spaCy模型
python -m spacy download en_core_web_sm
python -m spacy download zh_core_web_sm
python -m spacy download ja_core_news_sm

# 3. 運行應用
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📊 系統需求

### 最低配置
- **CPU**: 1 vCPU
- **記憶體**: 2GB RAM
- **儲存**: 1GB 磁碟空間
- **網路**: 穩定網路連接

### 推薦配置
- **CPU**: 2+ vCPU
- **記憶體**: 4GB+ RAM
- **儲存**: 5GB+ 磁碟空間

### Railway資源配置
```json
{
  "builder": "dockerfile",
  "healthcheckPath": "/health",
  "restartPolicyType": "on-failure",
  "restartPolicyMaxRetries": 3
}
```

## 🧪 功能測試

### API端點測試
```bash
# 健康檢查
curl https://your-app.railway.app/health

# 文檔頁面
curl https://your-app.railway.app/docs
```

### 集成測試
```bash
# 運行完整測試套件
python tests/test_integration.py
```

## 🐛 故障排除

### 常見問題

#### 1. spaCy模型下載失敗
```bash
# 手動下載模型
docker exec -it container-name python -m spacy download zh_core_web_sm
```

#### 2. 記憶體不足
```bash
# 檢查記憶體使用
railway logs | grep "memory"

# 升級Railway計畫
railway upgrade
```

#### 3. 依賴安裝失敗
```bash
# 檢查requirements.txt
cat requirements.txt

# 清理和重建
railway redeploy
```

#### 4. 端口衝突
```bash
# 檢查Dockerfile端口配置
grep EXPOSE Dockerfile

# 確認Railway端口映射
railway variables
```

### 日誌分析
```bash
# 實時日誌監控
railway logs --follow

# 錯誤日誌篩選
railway logs | grep ERROR

# 性能監控
railway metrics
```

## 🔐 安全性配置

### 環境變量管理
```bash
# 敏感信息配置
railway variables set SECRET_KEY="your-secret-key"
railway variables set DATABASE_URL="your-db-url"
```

### CORS設置
應用已配置基本CORS設置，生產環境建議調整：
```python
# 在app/main.py中修改
origins = ["https://your-frontend-domain.com"]
```

## 📈 性能優化

### Docker優化
- 多階段構建
- 最小化鏡像大小
- 有效的.dockerignore

### 應用優化
- 異步處理
- 連接池配置
- 快取策略

## 📞 支援與聯絡

### 技術支援
- 📧 Email: support@chempatent.com
- 📚 文檔: https://docs.chempatent.com
- 🐛 問題回報: https://github.com/yourusername/chempatent-pro/issues

### 版本資訊
- **版本**: v1.0.0
- **構建日期**: 2025-09-05
- **Python版本**: 3.11+
- **Docker版本**: 支援最新版本

---

## 📄 授權聲明

本項目採用 MIT 授權條款。詳情請參閱 LICENSE 文件。

---

**🎉 部署完成後，您的ChemPatent Pro系統將可在Railway提供的URL上訪問！**
