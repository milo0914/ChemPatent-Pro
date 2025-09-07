
import cv2
import numpy as np
from PIL import Image
import base64
import io
from typing import List, Dict, Optional, Tuple, Any
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors, rdDepictor, Draw, AllChem
from rdkit.Chem.Draw import rdMolDraw2D
import matplotlib.pyplot as plt
import re
from loguru import logger

class ChemicalStructureAnalyzer:
    """化學結構識別和SMILES轉換分析器"""

    def __init__(self):
        self.common_functional_groups = {
            'hydroxyl': r'-OH|OH',
            'carboxyl': r'-COOH|COOH',
            'amino': r'-NH2|NH2',
            'methyl': r'-CH3|CH3',
            'ethyl': r'-C2H5|C2H5',
            'phenyl': r'Ph|C6H5',
            'benzyl': r'Bn|C6H5CH2',
            'carbonyl': r'C=O',
            'ester': r'COO|OOC',
            'ether': r'-O-',
            'aldehyde': r'-CHO|CHO',
            'ketone': r'C=O',
            'nitro': r'-NO2|NO2',
            'sulfonate': r'-SO3|SO3',
            'phosphate': r'-PO4|PO4'
        }

    async def analyze_chemical_structure(self, image_data: bytes = None, text: str = None) -> Dict:
        """
        分析化學結構

        Args:
            image_data: 化學結構圖像數據
            text: 包含化學信息的文本

        Returns:
            分析結果字典
        """
        try:
            result = {
                'molecules': [],
                'functional_groups': [],
                'chemical_names': [],
                'smiles': [],
                'molecular_formulas': [],
                'analysis_methods': []
            }

            # 從文本中提取化學信息
            if text:
                logger.info("從文本中提取化學信息")
                text_analysis = await self._analyze_text_chemistry(text)
                result.update(text_analysis)

            # 從圖像中識別化學結構
            if image_data:
                logger.info("從圖像中識別化學結構")
                image_analysis = await self._analyze_image_chemistry(image_data)

                # 合併結果
                for key in ['molecules', 'smiles', 'molecular_formulas']:
                    if key in image_analysis:
                        result[key].extend(image_analysis[key])

            # 驗證和清理SMILES
            result['smiles'] = await self._validate_smiles(result['smiles'])

            # 生成分子描述符
            result['descriptors'] = await self._calculate_descriptors(result['smiles'])

            # 分析分子相似性
            result['similarity_analysis'] = await self._analyze_molecular_similarity(result['smiles'])

            logger.success(f"化學結構分析完成，識別出{len(result['smiles'])}個SMILES")
            return result

        except Exception as e:
            logger.error(f"化學結構分析失敗: {str(e)}")
            raise

    async def _analyze_text_chemistry(self, text: str) -> Dict:
        """從文本中提取化學信息"""
        result = {
            'molecules': [],
            'functional_groups': [],
            'chemical_names': [],
            'smiles': [],
            'molecular_formulas': []
        }

        # 提取SMILES字符串
        smiles_patterns = [
            r'[A-Za-z0-9\[\]()=#@+\-\\/\\]+',  # 基本SMILES模式
        ]

        for pattern in smiles_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if self._is_valid_smiles_pattern(match):
                    result['smiles'].append(match)

        # 提取分子式
        molecular_formula_patterns = [
            r'C\d+H\d+[A-Z]?\d*[A-Z]?\d*',  # 基本分子式
            r'[A-Z][a-z]?\d*(?:[A-Z][a-z]?\d*)*',  # 元素符號組合
        ]

        for pattern in molecular_formula_patterns:
            matches = re.findall(pattern, text)
            result['molecular_formulas'].extend(matches)

        # 提取化學名稱
        chemical_names = await self._extract_chemical_names(text)
        result['chemical_names'].extend(chemical_names)

        # 檢測官能團
        for group_name, pattern in self.common_functional_groups.items():
            if re.search(pattern, text, re.IGNORECASE):
                result['functional_groups'].append(group_name)

        return result

    def _is_valid_smiles_pattern(self, candidate: str) -> bool:
        """檢查是否為有效的SMILES模式"""
        # 基本SMILES字符檢查
        if len(candidate) < 3:
            return False

        # 包含SMILES常見字符
        smiles_chars = set('CNOSPFClBrI[]()=#@+-/\\')
        if not any(c in smiles_chars for c in candidate):
            return False

        # 不應該是純數字
        if candidate.isdigit():
            return False

        # 不應該包含空格
        if ' ' in candidate:
            return False

        return True

    async def _extract_chemical_names(self, text: str) -> List[str]:
        """提取化學名稱"""
        chemical_names = []

        # 常見化學後綴
        chemical_suffixes = [
            r'\w+ane\b',  # 烷烴
            r'\w+ene\b',  # 烯烴
            r'\w+yne\b',  # 炔烴
            r'\w+ol\b',   # 醇類
            r'\w+al\b',   # 醛類
            r'\w+one\b',  # 酮類
            r'\w+ic acid\b',  # 羧酸
            r'\w+ate\b',  # 酯類
            r'\w+ide\b',  # 鹽類
        ]

        for suffix_pattern in chemical_suffixes:
            matches = re.findall(suffix_pattern, text, re.IGNORECASE)
            chemical_names.extend(matches)

        # 常見化學前綴
        prefix_patterns = [
            r'\b(?:meth|eth|prop|but|pent|hex|hept|oct|non|dec)yl\w*',
            r'\b(?:phenyl|benzyl|tolyl)\w*',
            r'\b(?:hydroxy|amino|nitro|sulfo|phospho)\w*'
        ]

        for prefix_pattern in prefix_patterns:
            matches = re.findall(prefix_pattern, text, re.IGNORECASE)
            chemical_names.extend(matches)

        return list(set(chemical_names))

    async def _analyze_image_chemistry(self, image_data: bytes) -> Dict:
        """從圖像中分析化學結構"""
        result = {
            'molecules': [],
            'smiles': [],
            'molecular_formulas': [],
            'structure_features': []
        }

        try:
            # 載入圖像
            image = Image.open(io.BytesIO(image_data))
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # 檢測化學結構特徵
            features = await self._detect_chemical_features(cv_image)
            result['structure_features'] = features

            # 基於特徵推斷可能的化學結構
            inferred_structures = await self._infer_structures_from_features(features)
            result.update(inferred_structures)

        except Exception as e:
            logger.warning(f"圖像化學結構分析失敗: {str(e)}")

        return result

    async def _detect_chemical_features(self, image: np.ndarray) -> Dict:
        """檢測化學結構特徵"""
        features = {
            'bonds': [],
            'rings': [],
            'atoms': [],
            'functional_groups': []
        }

        try:
            # 轉為灰度圖
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # 邊緣檢測
            edges = cv2.Canny(gray, 50, 150)

            # 檢測直線（化學鍵）
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=10, maxLineGap=5)
            if lines is not None:
                features['bonds'] = len(lines)

            # 檢測圓形（可能的原子或環結構）
            circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=5, maxRadius=50)
            if circles is not None:
                features['rings'] = len(circles[0])

            # 檢測文字區域（可能的原子標記）
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            text_regions = 0
            for contour in contours:
                area = cv2.contourArea(contour)
                if 10 < area < 1000:  # 適合文字的大小
                    text_regions += 1
            features['atoms'] = text_regions

        except Exception as e:
            logger.warning(f"特徵檢測失敗: {str(e)}")

        return features

    async def _infer_structures_from_features(self, features: Dict) -> Dict:
        """基於特徵推斷化學結構"""
        result = {
            'smiles': [],
            'molecular_formulas': [],
            'structure_type': 'unknown'
        }

        bonds = features.get('bonds', 0)
        rings = features.get('rings', 0)
        atoms = features.get('atoms', 0)

        # 簡單的結構推斷邏輯
        if rings > 0:
            result['structure_type'] = 'cyclic'
            if rings == 1:
                result['smiles'].append('C1CCCCC1')  # 示例：環己烷
            elif rings > 1:
                result['smiles'].append('c1ccccc1')  # 示例：苯環
        elif bonds > 5:
            result['structure_type'] = 'complex'
        elif bonds > 0:
            result['structure_type'] = 'linear'
            result['smiles'].append('CCCCCC')  # 示例：己烷

        return result

    async def _validate_smiles(self, smiles_list: List[str]) -> List[str]:
        """驗證SMILES字符串"""
        valid_smiles = []

        for smiles in smiles_list:
            try:
                mol = Chem.MolFromSmiles(smiles)
                if mol is not None:
                    # 標準化SMILES
                    canonical_smiles = Chem.MolToSmiles(mol)
                    valid_smiles.append(canonical_smiles)
                else:
                    logger.warning(f"無效的SMILES: {smiles}")
            except Exception as e:
                logger.warning(f"SMILES驗證失敗 {smiles}: {str(e)}")

        return list(set(valid_smiles))

    async def _calculate_descriptors(self, smiles_list: List[str]) -> Dict:
        """計算分子描述符"""
        descriptors = {}

        for i, smiles in enumerate(smiles_list):
            try:
                mol = Chem.MolFromSmiles(smiles)
                if mol is not None:
                    desc = {
                        'molecular_weight': rdMolDescriptors.CalcExactMolWt(mol),
                        'logp': rdMolDescriptors.CalcCrippenDescriptors(mol)[0],
                        'hbd': rdMolDescriptors.CalcNumHBD(mol),  # 氫鍵供體
                        'hba': rdMolDescriptors.CalcNumHBA(mol),  # 氫鍵受體
                        'tpsa': rdMolDescriptors.CalcTPSA(mol),   # 拓撲極性表面積
                        'rotatable_bonds': rdMolDescriptors.CalcNumRotatableBonds(mol),
                        'ring_count': rdMolDescriptors.CalcNumRings(mol),
                        'aromatic_rings': rdMolDescriptors.CalcNumAromaticRings(mol)
                    }
                    descriptors[f'molecule_{i+1}'] = desc
            except Exception as e:
                logger.warning(f"計算描述符失敗 {smiles}: {str(e)}")

        return descriptors

    async def _analyze_molecular_similarity(self, smiles_list: List[str]) -> Dict:
        """分析分子相似性"""
        similarity_matrix = {}

        if len(smiles_list) < 2:
            return similarity_matrix

        try:
            mols = []
            fps = []

            for smiles in smiles_list:
                mol = Chem.MolFromSmiles(smiles)
                if mol is not None:
                    mols.append(mol)
                    fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2)
                    fps.append(fp)

            # 計算Tanimoto相似性
            for i in range(len(fps)):
                for j in range(i+1, len(fps)):
                    similarity = DataStructs.TanimotoSimilarity(fps[i], fps[j])
                    similarity_matrix[f'{i+1}_vs_{j+1}'] = similarity

        except Exception as e:
            logger.warning(f"相似性分析失敗: {str(e)}")

        return similarity_matrix

    async def generate_molecule_image(self, smiles: str, size: Tuple[int, int] = (300, 300)) -> bytes:
        """生成分子結構圖"""
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                raise ValueError(f"無效的SMILES: {smiles}")

            # 生成2D座標
            rdDepictor.Compute2DCoords(mol)

            # 創建分子圖像
            drawer = rdMolDraw2D.MolDraw2DCairo(size[0], size[1])
            drawer.DrawMolecule(mol)
            drawer.FinishDrawing()

            # 轉換為bytes
            img_data = drawer.GetDrawingText()
            return img_data

        except Exception as e:
            logger.error(f"生成分子圖像失敗: {str(e)}")
            raise

    async def smiles_to_molecular_formula(self, smiles: str) -> str:
        """將SMILES轉換為分子式"""
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is not None:
                return rdMolDescriptors.CalcMolFormula(mol)
            return ""
        except Exception as e:
            logger.warning(f"SMILES轉分子式失敗 {smiles}: {str(e)}")
            return ""

    async def predict_properties(self, smiles: str) -> Dict:
        """預測分子性質"""
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return {}

            properties = {
                'molecular_weight': rdMolDescriptors.CalcExactMolWt(mol),
                'formula': rdMolDescriptors.CalcMolFormula(mol),
                'logp': rdMolDescriptors.CalcCrippenDescriptors(mol)[0],
                'hbd': rdMolDescriptors.CalcNumHBD(mol),
                'hba': rdMolDescriptors.CalcNumHBA(mol),
                'tpsa': rdMolDescriptors.CalcTPSA(mol),
                'rotatable_bonds': rdMolDescriptors.CalcNumRotatableBonds(mol),
                'drug_like': self._assess_drug_likeness(mol),
                'lipinski_violations': self._count_lipinski_violations(mol)
            }

            return properties

        except Exception as e:
            logger.error(f"性質預測失敗: {str(e)}")
            return {}

    def _assess_drug_likeness(self, mol) -> bool:
        """評估藥物相似性（Lipinski五規則）"""
        try:
            mw = rdMolDescriptors.CalcExactMolWt(mol)
            logp = rdMolDescriptors.CalcCrippenDescriptors(mol)[0]
            hbd = rdMolDescriptors.CalcNumHBD(mol)
            hba = rdMolDescriptors.CalcNumHBA(mol)

            violations = 0
            if mw > 500: violations += 1
            if logp > 5: violations += 1
            if hbd > 5: violations += 1
            if hba > 10: violations += 1

            return violations <= 1
        except:
            return False

    def _count_lipinski_violations(self, mol) -> int:
        """計算Lipinski規則違反數"""
        try:
            violations = 0
            mw = rdMolDescriptors.CalcExactMolWt(mol)
            logp = rdMolDescriptors.CalcCrippenDescriptors(mol)[0]
            hbd = rdMolDescriptors.CalcNumHBD(mol)
            hba = rdMolDescriptors.CalcNumHBA(mol)

            if mw > 500: violations += 1
            if logp > 5: violations += 1
            if hbd > 5: violations += 1
            if hba > 10: violations += 1

            return violations
        except:
            return 0

# 創建全局實例
chem_analyzer = ChemicalStructureAnalyzer()
