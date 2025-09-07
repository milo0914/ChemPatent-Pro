
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import uvicorn
import os
from pathlib import Path

from app.api import endpoints
from app.core.config import settings
from app.core.logging import setup_logging

# 設置日誌
setup_logging()

# 創建FastAPI應用
app = FastAPI(
    title="ChemPatent Pro",
    description="化學專利分析系統 - 專業的化學專利文檔解析、分析和可視化平台",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS設置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 靜態文件服務
static_dir = Path(__file__).parent / "frontend" / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# 包含路由
app.include_router(endpoints.router, prefix="/api/v1")

# 健康檢查端點
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ChemPatent Pro",
        "version": "1.0.0"
    }

# 根路由 - 服務前端
@app.get("/", response_class=HTMLResponse)
async def read_root():
    template_path = Path(__file__).parent / "frontend" / "templates" / "index.html"
    if template_path.exists():
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return HTMLResponse(content='''
        <!DOCTYPE html>
        <html>
        <head>
            <title>ChemPatent Pro</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h1 { color: #2c3e50; text-align: center; margin-bottom: 30px; }
                .feature { margin: 20px 0; padding: 15px; border-left: 4px solid #3498db; background: #ecf0f1; }
                .api-link { display: block; text-align: center; margin: 20px 0; padding: 10px; background: #3498db; color: white; text-decoration: none; border-radius: 5px; }
                .api-link:hover { background: #2980b9; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🧪 ChemPatent Pro</h1>
                <p>歡迎使用ChemPatent Pro化學專利分析系統！</p>

                <div class="feature">
                    <h3>📄 多語言PDF解析</h3>
                    <p>支持中文、英文、日文專利文檔的智能解析</p>
                </div>

                <div class="feature">
                    <h3>🧬 化學結構識別</h3>
                    <p>自動識別化學結構並轉換為SMILES格式</p>
                </div>

                <div class="feature">
                    <h3>⚖️ 專利權利要求分析</h3>
                    <p>深度分析專利權利要求的結構和依賴關係</p>
                </div>

                <div class="feature">
                    <h3>📊 分子性質計算</h3>
                    <p>計算分子描述符並生成可視化圖表</p>
                </div>

                <a href="/docs" class="api-link">📚 API文檔</a>
                <a href="/redoc" class="api-link">📖 ReDoc文檔</a>
            </div>
        </body>
        </html>
        ''')

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=False
    )
