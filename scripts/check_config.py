#!/usr/bin/env python3
"""
ChemPatent Pro 系統配置檢查腳本
"""

import os
import sys
import subprocess
import importlib
from pathlib import Path

def check_python_version():
    """檢查Python版本"""
    version = sys.version_info
    print(f"🐍 Python版本: {version.major}.{version.minor}.{version.micro}")

    if version.major == 3 and version.minor >= 8:
        print("✅ Python版本符合要求 (>= 3.8)")
        return True
    else:
        print("❌ Python版本不符合要求 (需要 >= 3.8)")
        return False

def check_system_dependencies():
    """檢查系統依賴"""
    print("\n🔧 檢查系統依賴...")

    dependencies = {
        'tesseract': 'tesseract --version',
        'poppler': 'pdftoppm -h',
        'curl': 'curl --version'
    }

    results = {}
    for name, cmd in dependencies.items():
        try:
            subprocess.run(cmd.split(), capture_output=True, check=True)
            print(f"✅ {name} 已安裝")
            results[name] = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"❌ {name} 未安裝或無法訪問")
            results[name] = False

    return all(results.values())

def check_python_packages():
    """檢查Python包"""
    print("\n📦 檢查Python包...")

    critical_packages = [
        'fastapi', 'uvicorn', 'pydantic', 'rdkit', 
        'spacy', 'pandas', 'numpy', 'matplotlib',
        'plotly', 'PIL', 'cv2', 'sklearn'
    ]

    results = {}
    for package in critical_packages:
        try:
            if package == 'PIL':
                importlib.import_module('PIL')
            elif package == 'cv2':
                importlib.import_module('cv2')
            elif package == 'sklearn':
                importlib.import_module('sklearn')
            else:
                importlib.import_module(package)
            print(f"✅ {package}")
            results[package] = True
        except ImportError:
            print(f"❌ {package} 未安裝")
            results[package] = False

    return all(results.values())

def check_spacy_models():
    """檢查spaCy模型"""
    print("\n🌍 檢查spaCy語言模型...")

    models = ['en_core_web_sm', 'zh_core_web_sm', 'ja_core_news_sm']
    results = {}

    for model in models:
        try:
            import spacy
            nlp = spacy.load(model)
            print(f"✅ {model}")
            results[model] = True
        except OSError:
            print(f"❌ {model} 未安裝")
            results[model] = False
        except ImportError:
            print(f"❌ spaCy未安裝，無法檢查 {model}")
            results[model] = False

    return all(results.values())

def check_file_structure():
    """檢查文件結構"""
    print("\n📁 檢查項目文件結構...")

    base_path = Path(__file__).parent.parent
    required_files = [
        'app/main.py',
        'app/services/pdf_parser.py',
        'app/services/chemical_analyzer.py',
        'app/services/patent_analyzer.py',
        'app/services/molecular_visualizer.py',
        'frontend/templates/index.html',
        'frontend/static/js/main.js',
        'requirements.txt',
        'Dockerfile',
        'railway.json'
    ]

    results = {}
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
            results[file_path] = True
        else:
            print(f"❌ {file_path} 不存在")
            results[file_path] = False

    return all(results.values())

def check_directories():
    """檢查並創建必要目錄"""
    print("\n📂 檢查並創建必要目錄...")

    base_path = Path(__file__).parent.parent
    required_dirs = [
        'uploads',
        'logs',
        'tmp',
        'static/uploads'
    ]

    for dir_path in required_dirs:
        full_path = base_path / dir_path
        if not full_path.exists():
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ 創建目錄: {dir_path}")
        else:
            print(f"✅ 目錄存在: {dir_path}")

    return True

def main():
    """主檢查函數"""
    print("🔍 ChemPatent Pro 系統配置檢查\n")
    print("="*60)

    checks = [
        ("Python版本", check_python_version),
        ("系統依賴", check_system_dependencies),
        ("Python包", check_python_packages),
        ("spaCy模型", check_spacy_models),
        ("文件結構", check_file_structure),
        ("目錄結構", check_directories)
    ]

    passed = 0
    total = len(checks)

    for check_name, check_func in checks:
        print(f"\n{'-'*40}")
        print(f"檢查: {check_name}")
        print(f"{'-'*40}")

        try:
            if check_func():
                passed += 1
                print(f"✅ {check_name} 通過")
            else:
                print(f"❌ {check_name} 失敗")
        except Exception as e:
            print(f"❌ {check_name} 檢查錯誤: {e}")

    print(f"\n{'='*60}")
    print(f"檢查結果: {passed}/{total} 通過")
    print(f"{'='*60}")

    if passed == total:
        print("🎉 系統配置完整，可以部署！")
    elif passed >= total - 2:
        print("⚠️  大部分配置正確，建議修復後部署")
    else:
        print("❌ 系統配置不完整，需要修復後才能部署")

    return passed == total

if __name__ == "__main__":
    main()
