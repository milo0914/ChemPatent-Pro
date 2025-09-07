#!/usr/bin/env python3
"""
ChemPatent Pro 系統集成測試腳本
"""

import sys
import os
import json
import asyncio
from pathlib import Path

# 添加項目路徑到Python路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_imports():
    """測試所有核心模組是否能正常導入"""
    try:
        print("🔍 測試模組導入...")

        # 測試FastAPI主應用
        from app.main import app
        print("✅ FastAPI主應用導入成功")

        # 測試PDF解析服務
        from app.services.pdf_parser import PDFParser
        print("✅ PDF解析服務導入成功")

        # 測試化學分析器
        from app.services.chemical_analyzer import ChemicalAnalyzer
        print("✅ 化學分析器導入成功")

        # 測試專利分析器
        from app.services.patent_analyzer import PatentAnalyzer
        print("✅ 專利分析器導入成功")

        # 測試分子可視化器
        from app.services.molecular_visualizer import MolecularVisualizer
        print("✅ 分子可視化器導入成功")

        return True

    except ImportError as e:
        print(f"❌ 導入錯誤: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他錯誤: {e}")
        return False

async def test_basic_functionality():
    """測試基本功能"""
    try:
        print("\n🔍 測試基本功能...")

        # 測試化學分析器基本功能
        from app.services.chemical_analyzer import ChemicalAnalyzer
        analyzer = ChemicalAnalyzer()

        # 測試SMILES驗證
        test_smiles = "CCO"  # 乙醇
        result = await analyzer.validate_smiles(test_smiles)
        if result.get("valid"):
            print(f"✅ SMILES驗證測試通過: {test_smiles}")
        else:
            print(f"❌ SMILES驗證測試失敗: {test_smiles}")
            return False

        # 測試分子可視化器
        from app.services.molecular_visualizer import MolecularVisualizer
        visualizer = MolecularVisualizer()

        # 測試分子性質計算
        properties = await visualizer.calculate_molecular_properties(test_smiles)
        if properties and "molecular_weight" in properties:
            print(f"✅ 分子性質計算測試通過")
        else:
            print("❌ 分子性質計算測試失敗")
            return False

        return True

    except Exception as e:
        print(f"❌ 基本功能測試錯誤: {e}")
        return False

async def test_api_endpoints():
    """測試API端點"""
    try:
        print("\n🔍 測試API端點...")

        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)

        # 測試健康檢查端點
        response = client.get("/health")
        if response.status_code == 200:
            print("✅ 健康檢查端點測試通過")
        else:
            print(f"❌ 健康檢查端點測試失敗: {response.status_code}")
            return False

        # 測試根端點
        response = client.get("/")
        if response.status_code == 200:
            print("✅ 根端點測試通過")
        else:
            print(f"❌ 根端點測試失敗: {response.status_code}")
            return False

        return True

    except Exception as e:
        print(f"❌ API端點測試錯誤: {e}")
        return False

async def main():
    """主測試函數"""
    print("🚀 ChemPatent Pro 系統集成測試開始\n")

    # 執行所有測試
    tests = [
        ("模組導入測試", test_imports),
        ("基本功能測試", test_basic_functionality),
        ("API端點測試", test_api_endpoints)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"執行 {test_name}")
        print(f"{'='*50}")

        try:
            result = await test_func()
            if result:
                passed += 1
                print(f"\n✅ {test_name} 通過")
            else:
                print(f"\n❌ {test_name} 失敗")
        except Exception as e:
            print(f"\n❌ {test_name} 執行錯誤: {e}")

    print(f"\n{'='*50}")
    print(f"測試結果: {passed}/{total} 通過")
    print(f"{'='*50}")

    if passed == total:
        print("🎉 所有測試通過！系統準備就緒。")
        return True
    else:
        print("⚠️  存在測試失敗，請檢查系統配置。")
        return False

if __name__ == "__main__":
    asyncio.run(main())
