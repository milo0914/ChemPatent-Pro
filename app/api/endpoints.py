
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Optional, Dict, Any
import asyncio
import tempfile
import os
from pathlib import Path

from app.services.pdf_parser import pdf_parser
from app.services.chemical_analyzer import chem_analyzer
from app.services.patent_analyzer import patent_analyzer
from app.services.molecular_visualizer import molecular_calculator
from app.models.schemas import *
from app.core.config import settings
from loguru import logger

router = APIRouter()

# PDF解析端點
@router.post("/parse-pdf", response_model=PDFParseResponse)
async def parse_pdf(
    file: UploadFile = File(...),
    language: str = Form("auto")
):
    """解析PDF文檔"""
    try:
        # 驗證文件類型
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="僅支持PDF文件")

        # 檢查文件大小
        content = await file.read()
        if len(content) > settings.MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="文件過大")

        logger.info(f"開始解析PDF文件: {file.filename}")

        # 解析PDF
        result = await pdf_parser.parse_pdf(content, language)

        return PDFParseResponse(
            success=True,
            filename=file.filename,
            language=result['detected_language'],
            page_count=result['page_count'],
            extraction_method=result['extraction_method'],
            text_content=result['text_content'],
            metadata=result['metadata'],
            structure=result['structure']
        )

    except Exception as e:
        logger.error(f"PDF解析失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"PDF解析失敗: {str(e)}")

# 化學結構分析端點
@router.post("/analyze-chemistry", response_model=ChemicalAnalysisResponse)
async def analyze_chemistry(
    text: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None)
):
    """分析化學結構"""
    try:
        if not text and not image:
            raise HTTPException(status_code=400, detail="必須提供文本或圖像")

        image_data = None
        if image:
            if not any(image.filename.lower().endswith(ext) 
                      for ext in ['.png', '.jpg', '.jpeg']):
                raise HTTPException(status_code=400, detail="僅支持PNG/JPG圖像")

            image_data = await image.read()

        logger.info("開始化學結構分析")

        result = await chem_analyzer.analyze_chemical_structure(
            image_data=image_data,
            text=text
        )

        return ChemicalAnalysisResponse(
            success=True,
            molecules_found=len(result['smiles']),
            smiles=result['smiles'],
            molecular_formulas=result['molecular_formulas'],
            chemical_names=result['chemical_names'],
            functional_groups=result['functional_groups'],
            descriptors=result['descriptors'],
            similarity_analysis=result['similarity_analysis']
        )

    except Exception as e:
        logger.error(f"化學結構分析失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"化學結構分析失敗: {str(e)}")

# 專利權利要求分析端點
@router.post("/analyze-patent-claims", response_model=PatentClaimsAnalysisResponse)
async def analyze_patent_claims(
    text: str = Form(...),
    language: str = Form("auto")
):
    """分析專利權利要求"""
    try:
        logger.info("開始專利權利要求分析")

        result = await patent_analyzer.analyze_patent_claims(text, language)

        return PatentClaimsAnalysisResponse(
            success=True,
            total_claims=result['total_claims'],
            language=result['language'],
            claims=result['claims'],
            structure_analysis=result['structure_analysis'],
            dependency_tree=result['dependency_tree'],
            technical_features=result['technical_features'],
            innovations=result['innovations'],
            coverage_scope=result['coverage_scope'],
            potential_issues=result['potential_issues'],
            suggestions=result['suggestions'],
            analysis_summary=result['analysis_summary']
        )

    except Exception as e:
        logger.error(f"專利分析失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"專利分析失敗: {str(e)}")

# 分子性質計算端點
@router.post("/calculate-molecular-properties", response_model=MolecularPropertiesResponse)
async def calculate_molecular_properties(
    smiles_list: List[str] = Form(...)
):
    """計算分子性質"""
    try:
        if len(smiles_list) > settings.MAX_MOLECULES_PER_REQUEST:
            raise HTTPException(
                status_code=400, 
                detail=f"一次最多處理{settings.MAX_MOLECULES_PER_REQUEST}個分子"
            )

        logger.info(f"開始計算{len(smiles_list)}個分子的性質")

        result = await molecular_calculator.calculate_all_properties(smiles_list)

        return MolecularPropertiesResponse(
            success=True,
            molecules_count=len(result['molecules']),
            molecules=result['molecules'],
            properties_summary=result['properties_summary'],
            comparisons=result['comparisons'],
            visualizations=result['visualizations']
        )

    except Exception as e:
        logger.error(f"分子性質計算失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分子性質計算失敗: {str(e)}")

# 生成分子結構圖端點
@router.get("/molecule-image/{smiles}")
async def generate_molecule_image(smiles: str, width: int = 300, height: int = 300):
    """生成分子結構圖"""
    try:
        image_data = await chem_analyzer.generate_molecule_image(smiles, (width, height))

        # 創建臨時文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            temp_file.write(image_data)
            temp_path = temp_file.name

        return FileResponse(
            temp_path,
            media_type="image/png",
            filename=f"molecule_{smiles[:10]}.png",
            background=BackgroundTasks([lambda: os.unlink(temp_path)])
        )

    except Exception as e:
        logger.error(f"分子圖像生成失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分子圖像生成失敗: {str(e)}")

# 綜合分析端點
@router.post("/comprehensive-analysis", response_model=ComprehensiveAnalysisResponse)
async def comprehensive_analysis(
    pdf_file: UploadFile = File(...),
    language: str = Form("auto"),
    include_molecular_analysis: bool = Form(True),
    include_patent_analysis: bool = Form(True)
):
    """綜合分析 - PDF解析 + 化學分析 + 專利分析"""
    try:
        logger.info(f"開始綜合分析: {pdf_file.filename}")

        # 1. PDF解析
        content = await pdf_file.read()
        pdf_result = await pdf_parser.parse_pdf(content, language)

        # 提取全文
        full_text = ""
        for page in pdf_result['text_content']['pages']:
            full_text += page.get('text', '') + "\n"

        response = ComprehensiveAnalysisResponse(
            success=True,
            filename=pdf_file.filename,
            pdf_analysis=pdf_result
        )

        # 2. 化學結構分析（如果請求）
        if include_molecular_analysis:
            try:
                chem_result = await chem_analyzer.analyze_chemical_structure(text=full_text)
                response.chemical_analysis = chem_result

                # 如果找到SMILES，計算分子性質
                if chem_result['smiles']:
                    mol_props = await molecular_calculator.calculate_all_properties(
                        chem_result['smiles'][:10]  # 限制數量
                    )
                    response.molecular_properties = mol_props

            except Exception as e:
                logger.warning(f"化學分析失敗: {str(e)}")

        # 3. 專利權利要求分析（如果請求）
        if include_patent_analysis:
            try:
                patent_result = await patent_analyzer.analyze_patent_claims(
                    full_text, pdf_result['detected_language']
                )
                response.patent_analysis = patent_result

            except Exception as e:
                logger.warning(f"專利分析失敗: {str(e)}")

        logger.success("綜合分析完成")
        return response

    except Exception as e:
        logger.error(f"綜合分析失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"綜合分析失敗: {str(e)}")

# 健康檢查端點
@router.get("/health")
async def api_health():
    """API健康檢查"""
    return {
        "status": "healthy",
        "api_version": "v1",
        "endpoints": [
            "/parse-pdf",
            "/analyze-chemistry", 
            "/analyze-patent-claims",
            "/calculate-molecular-properties",
            "/molecule-image/{smiles}",
            "/comprehensive-analysis"
        ]
    }
