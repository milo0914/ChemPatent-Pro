
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

# 基礎響應模型
class BaseResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# PDF解析相關模型
class PDFParseResponse(BaseResponse):
    filename: str
    language: str
    page_count: int
    extraction_method: str
    text_content: Dict[str, Any]
    metadata: Dict[str, Any]
    structure: Dict[str, Any]

# 化學分析相關模型
class ChemicalAnalysisResponse(BaseResponse):
    molecules_found: int
    smiles: List[str]
    molecular_formulas: List[str]
    chemical_names: List[str]
    functional_groups: List[str]
    descriptors: Dict[str, Any]
    similarity_analysis: Dict[str, Any]

# 專利分析相關模型
class PatentClaim(BaseModel):
    number: int
    text: str
    type: str
    word_count: int
    complexity_score: float

class PatentClaimsAnalysisResponse(BaseResponse):
    total_claims: int
    language: str
    claims: List[PatentClaim]
    structure_analysis: Dict[str, Any]
    dependency_tree: Dict[str, Any]
    technical_features: Dict[str, Any]
    innovations: Dict[str, Any]
    coverage_scope: Dict[str, Any]
    potential_issues: List[Dict[str, Any]]
    suggestions: List[str]
    analysis_summary: Dict[str, Any]

# 分子性質相關模型
class MoleculeProperties(BaseModel):
    id: str
    smiles: str
    basic_properties: Dict[str, Any]
    physicochemical_properties: Dict[str, Any]
    drug_like_properties: Dict[str, Any]
    admet_properties: Dict[str, Any]
    fingerprints: Dict[str, Any]

class MolecularPropertiesResponse(BaseResponse):
    molecules_count: int
    molecules: List[MoleculeProperties]
    properties_summary: Dict[str, Any]
    comparisons: Dict[str, Any]
    visualizations: Dict[str, Any]

# 綜合分析響應模型
class ComprehensiveAnalysisResponse(BaseResponse):
    filename: str
    pdf_analysis: Dict[str, Any]
    chemical_analysis: Optional[Dict[str, Any]] = None
    patent_analysis: Optional[Dict[str, Any]] = None
    molecular_properties: Optional[Dict[str, Any]] = None

# 請求模型
class ChemicalAnalysisRequest(BaseModel):
    text: Optional[str] = None
    smiles_list: Optional[List[str]] = None
    include_visualization: bool = True

class PatentAnalysisRequest(BaseModel):
    text: str
    language: str = "auto"
    include_technical_features: bool = True
    include_innovations: bool = True

class MolecularPropertiesRequest(BaseModel):
    smiles_list: List[str]
    include_visualization: bool = True
    include_admet: bool = True

# 錯誤響應模型
class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# 文件上傳響應
class FileUploadResponse(BaseResponse):
    filename: str
    file_size: int
    file_type: str
    upload_path: str
