
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors, Draw, AllChem, Descriptors
from rdkit.Chem.Draw import rdMolDraw2D
from rdkit.Chem.Fingerprints import FingerprintMols
from rdkit.Chem.AtomPairs import Pairs
from rdkit.Chem.Pharm2D.SigFactory import SigFactory
from rdkit.Chem.Pharm2D import Generate
import io
import base64
from typing import List, Dict, Optional, Tuple, Any
from loguru import logger
import json

class MolecularPropertyCalculator:
    """分子性質計算和可視化器"""

    def __init__(self):
        # 分子描述符類別
        self.descriptor_categories = {
            'basic': ['molecular_weight', 'formula', 'num_atoms', 'num_bonds'],
            'lipophilicity': ['logp', 'logd', 'mlogp'],
            'solubility': ['tpsa', 'hbd', 'hba', 'rotatable_bonds'],
            'drug_like': ['lipinski_violations', 'qed', 'sa_score'],
            'toxicity': ['ames_mutagenicity', 'hepatotoxicity', 'skin_sensitization'],
            'stability': ['stability_score', 'synthetic_accessibility']
        }

        # 圖表顏色調色板
        self.color_palette = px.colors.qualitative.Set3

    async def calculate_all_properties(self, smiles_list: List[str]) -> Dict:
        """
        計算所有分子性質

        Args:
            smiles_list: SMILES字符串列表

        Returns:
            包含所有性質的字典
        """
        try:
            logger.info(f"開始計算{len(smiles_list)}個分子的性質")

            results = {
                'molecules': [],
                'properties_summary': {},
                'comparisons': {},
                'visualizations': {}
            }

            # 為每個分子計算性質
            for i, smiles in enumerate(smiles_list):
                try:
                    mol_properties = await self._calculate_single_molecule_properties(smiles, f"molecule_{i+1}")
                    results['molecules'].append(mol_properties)
                except Exception as e:
                    logger.warning(f"計算分子{i+1}性質失敗: {str(e)}")
                    continue

            if results['molecules']:
                # 生成統計摘要
                results['properties_summary'] = await self._generate_properties_summary(results['molecules'])

                # 分子間比較
                results['comparisons'] = await self._compare_molecules(results['molecules'])

                # 生成可視化圖表
                results['visualizations'] = await self._generate_visualizations(results['molecules'])

            logger.success(f"成功計算{len(results['molecules'])}個分子的性質")
            return results

        except Exception as e:
            logger.error(f"分子性質計算失敗: {str(e)}")
            raise

    async def _calculate_single_molecule_properties(self, smiles: str, mol_id: str) -> Dict:
        """計算單個分子的所有性質"""
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError(f"無效的SMILES: {smiles}")

        properties = {
            'id': mol_id,
            'smiles': smiles,
            'basic_properties': {},
            'physicochemical_properties': {},
            'drug_like_properties': {},
            'admet_properties': {},
            'fingerprints': {}
        }

        # 基本性質
        properties['basic_properties'] = {
            'molecular_weight': round(Descriptors.MolWt(mol), 2),
            'molecular_formula': rdMolDescriptors.CalcMolFormula(mol),
            'num_atoms': mol.GetNumAtoms(),
            'num_bonds': mol.GetNumBonds(),
            'num_rings': rdMolDescriptors.CalcNumRings(mol),
            'num_aromatic_rings': rdMolDescriptors.CalcNumAromaticRings(mol),
            'num_heavy_atoms': mol.GetNumHeavyAtoms()
        }

        # 理化性質
        properties['physicochemical_properties'] = {
            'logp': round(Descriptors.MolLogP(mol), 2),
            'tpsa': round(Descriptors.TPSA(mol), 2),
            'hbd': Descriptors.NumHDonors(mol),
            'hba': Descriptors.NumHAcceptors(mol),
            'rotatable_bonds': Descriptors.NumRotatableBonds(mol),
            'formal_charge': Chem.rdmolops.GetFormalCharge(mol),
            'refractivity': round(Descriptors.MolMR(mol), 2),
            'polarizability': round(Descriptors.BalabanJ(mol), 2) if Descriptors.BalabanJ(mol) else 0
        }

        # 類藥性質
        lipinski_violations = self._count_lipinski_violations(mol)
        properties['drug_like_properties'] = {
            'lipinski_violations': lipinski_violations,
            'lipinski_compliant': lipinski_violations == 0,
            'qed_score': round(self._calculate_qed(mol), 3),
            'sa_score': round(self._calculate_sa_score(mol), 3),
            'bioavailability_score': round(self._calculate_bioavailability_score(mol), 3)
        }

        # ADMET性質（簡化版）
        properties['admet_properties'] = {
            'bbb_permeant': self._predict_bbb_permeation(mol),
            'pgp_substrate': self._predict_pgp_substrate(mol),
            'cyp_inhibitor': self._predict_cyp_inhibition(mol),
            'ames_mutagenicity': self._predict_ames_mutagenicity(mol),
            'hepatotoxicity': self._predict_hepatotoxicity(mol)
        }

        # 分子指紋
        properties['fingerprints'] = {
            'morgan_fp': list(AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=1024).ToBitString()),
            'maccs_fp': list(rdMolDescriptors.GetMACCSKeysFingerprint(mol).ToBitString()) if hasattr(rdMolDescriptors, 'GetMACCSKeysFingerprint') else [],
            'atom_pairs': len(Pairs.GetAtomPairFingerprint(mol).GetNonzeroElements())
        }

        return properties

    def _count_lipinski_violations(self, mol) -> int:
        """計算Lipinski五規則違反數"""
        violations = 0

        mw = Descriptors.MolWt(mol)
        logp = Descriptors.MolLogP(mol)
        hbd = Descriptors.NumHDonors(mol)
        hba = Descriptors.NumHAcceptors(mol)

        if mw > 500: violations += 1
        if logp > 5: violations += 1
        if hbd > 5: violations += 1
        if hba > 10: violations += 1

        return violations

    def _calculate_qed(self, mol) -> float:
        """計算QED (Quantitative Estimate of Drug-likeness)"""
        # 簡化的QED計算
        try:
            mw = Descriptors.MolWt(mol)
            logp = Descriptors.MolLogP(mol)
            hbd = Descriptors.NumHDonors(mol)
            hba = Descriptors.NumHAcceptors(mol)
            tpsa = Descriptors.TPSA(mol)
            rotb = Descriptors.NumRotatableBonds(mol)

            # 標準化分數 (簡化版)
            mw_score = 1.0 if 150 <= mw <= 500 else max(0, 1 - abs(mw - 325) / 325)
            logp_score = 1.0 if -2 <= logp <= 5 else max(0, 1 - abs(logp - 1.5) / 3.5)
            hbd_score = 1.0 if hbd <= 5 else max(0, 1 - (hbd - 5) / 5)
            hba_score = 1.0 if hba <= 10 else max(0, 1 - (hba - 10) / 10)
            tpsa_score = 1.0 if tpsa <= 140 else max(0, 1 - (tpsa - 140) / 140)
            rotb_score = 1.0 if rotb <= 10 else max(0, 1 - (rotb - 10) / 10)

            # 幾何平均
            qed = (mw_score * logp_score * hbd_score * hba_score * tpsa_score * rotb_score) ** (1/6)
            return qed

        except Exception as e:
            logger.warning(f"QED計算失敗: {str(e)}")
            return 0.0

    def _calculate_sa_score(self, mol) -> float:
        """計算合成可及性分數"""
        # 簡化的SA分數計算
        try:
            # 基於分子複雜性的簡單估算
            num_rings = rdMolDescriptors.CalcNumRings(mol)
            num_chiral = rdMolDescriptors.CalcNumAtomStereoCenters(mol)
            num_rotatable = Descriptors.NumRotatableBonds(mol)
            mol_wt = Descriptors.MolWt(mol)

            complexity = (num_rings * 0.1 + num_chiral * 0.2 + 
                         num_rotatable * 0.05 + mol_wt / 1000)

            # 轉換為1-10分數 (1=易合成, 10=難合成)
            sa_score = min(10, max(1, 1 + complexity * 3))
            return sa_score

        except Exception as e:
            logger.warning(f"SA分數計算失敗: {str(e)}")
            return 5.0

    def _calculate_bioavailability_score(self, mol) -> float:
        """計算生物利用度分數"""
        # 基於Abbott Bioavailability Score
        try:
            mw = Descriptors.MolWt(mol)
            tpsa = Descriptors.TPSA(mol)

            score = 0.0
            if mw <= 500: score += 0.25
            if tpsa <= 140: score += 0.25
            if Descriptors.NumHDonors(mol) <= 5: score += 0.25
            if Descriptors.NumHAcceptors(mol) <= 10: score += 0.25

            return score

        except Exception as e:
            logger.warning(f"生物利用度分數計算失敗: {str(e)}")
            return 0.0

    def _predict_bbb_permeation(self, mol) -> bool:
        """預測血腦屏障穿透性"""
        # 簡化的BBB穿透預測
        try:
            mw = Descriptors.MolWt(mol)
            logp = Descriptors.MolLogP(mol)
            tpsa = Descriptors.TPSA(mol)

            # 基本規則
            return (mw < 450 and 0 < logp < 3 and tpsa < 90)

        except:
            return False

    def _predict_pgp_substrate(self, mol) -> bool:
        """預測P-糖蛋白底物"""
        # 簡化的P-gp預測
        try:
            mw = Descriptors.MolWt(mol)
            logp = Descriptors.MolLogP(mol)

            return (mw > 400 and logp > 2)

        except:
            return False

    def _predict_cyp_inhibition(self, mol) -> Dict[str, bool]:
        """預測CYP抑制"""
        # 簡化的CYP抑制預測
        try:
            mw = Descriptors.MolWt(mol)
            logp = Descriptors.MolLogP(mol)

            return {
                'cyp1a2': mw > 300 and logp > 2,
                'cyp2c9': mw > 250 and logp > 1,
                'cyp2c19': mw > 280 and logp > 1.5,
                'cyp2d6': mw > 200 and logp > 0,
                'cyp3a4': mw > 350 and logp > 3
            }

        except:
            return {cyp: False for cyp in ['cyp1a2', 'cyp2c9', 'cyp2c19', 'cyp2d6', 'cyp3a4']}

    def _predict_ames_mutagenicity(self, mol) -> bool:
        """預測Ames致突變性"""
        # 簡化的Ames預測 - 基於結構警報
        try:
            smiles = Chem.MolToSmiles(mol)

            # 常見致突變結構片段
            mutagenic_patterns = [
                r'N=N',  # 重氮化合物
                r'N\+.*O\-',  # 硝基化合物
                r'c1cc.*N.*cc1',  # 芳香胺
            ]

            for pattern in mutagenic_patterns:
                if pattern in smiles:
                    return True

            return False

        except:
            return False

    def _predict_hepatotoxicity(self, mol) -> bool:
        """預測肝毒性"""
        # 簡化的肝毒性預測
        try:
            # 基於分子量和logP的簡單規則
            mw = Descriptors.MolWt(mol)
            logp = Descriptors.MolLogP(mol)

            return (mw > 600 or logp > 6)

        except:
            return False

    async def _generate_properties_summary(self, molecules: List[Dict]) -> Dict:
        """生成性質統計摘要"""
        summary = {
            'count': len(molecules),
            'statistics': {},
            'distributions': {},
            'compliance_rates': {}
        }

        # 收集所有數值性質
        numeric_properties = [
            'molecular_weight', 'logp', 'tpsa', 'hbd', 'hba', 
            'rotatable_bonds', 'num_rings', 'qed_score', 'sa_score'
        ]

        for prop in numeric_properties:
            values = []
            for mol in molecules:
                if prop in mol['basic_properties']:
                    values.append(mol['basic_properties'][prop])
                elif prop in mol['physicochemical_properties']:
                    values.append(mol['physicochemical_properties'][prop])
                elif prop in mol['drug_like_properties']:
                    values.append(mol['drug_like_properties'][prop])

            if values:
                summary['statistics'][prop] = {
                    'mean': round(np.mean(values), 2),
                    'std': round(np.std(values), 2),
                    'min': min(values),
                    'max': max(values),
                    'median': round(np.median(values), 2)
                }

        # 計算合規率
        lipinski_compliant = sum(1 for mol in molecules 
                               if mol['drug_like_properties']['lipinski_compliant'])
        summary['compliance_rates']['lipinski'] = round(lipinski_compliant / len(molecules), 3)

        return summary

    async def _compare_molecules(self, molecules: List[Dict]) -> Dict:
        """分子間比較"""
        comparisons = {
            'similarity_matrix': {},
            'ranking': {},
            'clustering': {}
        }

        if len(molecules) < 2:
            return comparisons

        # 生成相似性矩陣 (基於性質相似性)
        similarity_matrix = np.zeros((len(molecules), len(molecules)))

        for i in range(len(molecules)):
            for j in range(i+1, len(molecules)):
                similarity = self._calculate_property_similarity(molecules[i], molecules[j])
                similarity_matrix[i][j] = similarity_matrix[j][i] = similarity

        comparisons['similarity_matrix'] = similarity_matrix.tolist()

        # 藥物相似性排名
        drug_scores = []
        for mol in molecules:
            score = mol['drug_like_properties']['qed_score']
            drug_scores.append((mol['id'], score))

        comparisons['ranking']['drug_likeness'] = sorted(drug_scores, 
                                                       key=lambda x: x[1], reverse=True)

        return comparisons

    def _calculate_property_similarity(self, mol1: Dict, mol2: Dict) -> float:
        """計算兩個分子的性質相似性"""
        # 基於關鍵性質的歐幾里得距離
        try:
            props = ['molecular_weight', 'logp', 'tpsa', 'hbd', 'hba']

            diff_sum = 0
            count = 0

            for prop in props:
                val1 = None
                val2 = None

                # 查找性質值
                for category in ['basic_properties', 'physicochemical_properties']:
                    if prop in mol1.get(category, {}):
                        val1 = mol1[category][prop]
                    if prop in mol2.get(category, {}):
                        val2 = mol2[category][prop]

                if val1 is not None and val2 is not None:
                    # 標準化差異
                    if prop == 'molecular_weight':
                        diff = abs(val1 - val2) / 500  # 標準化到500Da
                    elif prop == 'logp':
                        diff = abs(val1 - val2) / 5    # 標準化到5
                    elif prop == 'tpsa':
                        diff = abs(val1 - val2) / 140  # 標準化到140
                    else:
                        diff = abs(val1 - val2) / 10   # 默認標準化

                    diff_sum += diff ** 2
                    count += 1

            if count > 0:
                euclidean_dist = np.sqrt(diff_sum / count)
                similarity = 1 / (1 + euclidean_dist)  # 轉換為相似性分數
                return similarity

        except Exception as e:
            logger.warning(f"相似性計算失敗: {str(e)}")

        return 0.0

    async def _generate_visualizations(self, molecules: List[Dict]) -> Dict:
        """生成可視化圖表"""
        visualizations = {}

        try:
            # 1. 性質分布圖
            visualizations['property_distributions'] = await self._create_property_distribution_plots(molecules)

            # 2. 分子比較雷達圖
            visualizations['radar_charts'] = await self._create_radar_charts(molecules)

            # 3. 相關性熱力圖
            visualizations['correlation_heatmap'] = await self._create_correlation_heatmap(molecules)

            # 4. 類藥性分析圖
            visualizations['drug_likeness_analysis'] = await self._create_drug_likeness_plots(molecules)

            # 5. ADMET預測圖
            visualizations['admet_predictions'] = await self._create_admet_plots(molecules)

        except Exception as e:
            logger.error(f"可視化生成失敗: {str(e)}")

        return visualizations

    async def _create_property_distribution_plots(self, molecules: List[Dict]) -> str:
        """創建性質分布圖"""
        try:
            fig = make_subplots(
                rows=2, cols=3,
                subplot_titles=['分子量分布', 'LogP分布', 'TPSA分布', 
                               '氫鍵供體', '氫鍵受體', '可旋轉鍵'],
                specs=[[{'type': 'histogram'}, {'type': 'histogram'}, {'type': 'histogram'}],
                       [{'type': 'histogram'}, {'type': 'histogram'}, {'type': 'histogram'}]]
            )

            properties = [
                ('molecular_weight', 'basic_properties', 1, 1),
                ('logp', 'physicochemical_properties', 1, 2),
                ('tpsa', 'physicochemical_properties', 1, 3),
                ('hbd', 'physicochemical_properties', 2, 1),
                ('hba', 'physicochemical_properties', 2, 2),
                ('rotatable_bonds', 'physicochemical_properties', 2, 3)
            ]

            for prop, category, row, col in properties:
                values = [mol[category][prop] for mol in molecules if prop in mol[category]]

                if values:
                    fig.add_trace(
                        go.Histogram(x=values, name=prop, showlegend=False),
                        row=row, col=col
                    )

            fig.update_layout(
                title='分子性質分布',
                height=600,
                template='plotly_white'
            )

            return fig.to_html(include_plotlyjs='cdn')

        except Exception as e:
            logger.error(f"性質分布圖創建失敗: {str(e)}")
            return ""

    async def _create_radar_charts(self, molecules: List[Dict]) -> str:
        """創建雷達圖"""
        try:
            if len(molecules) > 5:  # 限制顯示數量
                molecules = molecules[:5]

            fig = go.Figure()

            categories = ['分子量 (標準化)', 'LogP', 'TPSA (標準化)', 
                         'HBD', 'HBA', 'QED分數']

            for mol in molecules:
                # 標準化數值到0-1範圍
                mw_norm = min(mol['basic_properties']['molecular_weight'] / 500, 1)
                tpsa_norm = min(mol['physicochemical_properties']['tpsa'] / 140, 1)

                values = [
                    mw_norm,
                    mol['physicochemical_properties']['logp'] / 5,
                    tpsa_norm,
                    mol['physicochemical_properties']['hbd'] / 5,
                    mol['physicochemical_properties']['hba'] / 10,
                    mol['drug_like_properties']['qed_score']
                ]

                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=categories,
                    fill='toself',
                    name=mol['id']
                ))

            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1]
                    )),
                title='分子性質雷達圖',
                template='plotly_white'
            )

            return fig.to_html(include_plotlyjs='cdn')

        except Exception as e:
            logger.error(f"雷達圖創建失敗: {str(e)}")
            return ""

    async def _create_correlation_heatmap(self, molecules: List[Dict]) -> str:
        """創建相關性熱力圖"""
        try:
            # 準備數據
            properties = ['molecular_weight', 'logp', 'tpsa', 'hbd', 'hba', 'rotatable_bonds']
            data = []

            for mol in molecules:
                row = []
                for prop in properties:
                    if prop in mol['basic_properties']:
                        row.append(mol['basic_properties'][prop])
                    elif prop in mol['physicochemical_properties']:
                        row.append(mol['physicochemical_properties'][prop])
                    else:
                        row.append(0)
                data.append(row)

            df = pd.DataFrame(data, columns=properties)
            corr_matrix = df.corr()

            fig = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale='RdBu',
                zmid=0
            ))

            fig.update_layout(
                title='分子性質相關性',
                template='plotly_white'
            )

            return fig.to_html(include_plotlyjs='cdn')

        except Exception as e:
            logger.error(f"相關性熱力圖創建失敗: {str(e)}")
            return ""

    async def _create_drug_likeness_plots(self, molecules: List[Dict]) -> str:
        """創建類藥性分析圖"""
        try:
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=['Lipinski規則合規性', 'QED分數分布'],
                specs=[[{'type': 'bar'}, {'type': 'histogram'}]]
            )

            # Lipinski合規性
            compliant = sum(1 for mol in molecules 
                          if mol['drug_like_properties']['lipinski_compliant'])
            non_compliant = len(molecules) - compliant

            fig.add_trace(
                go.Bar(x=['合規', '不合規'], y=[compliant, non_compliant],
                      marker_color=['green', 'red']),
                row=1, col=1
            )

            # QED分數分布
            qed_scores = [mol['drug_like_properties']['qed_score'] for mol in molecules]
            fig.add_trace(
                go.Histogram(x=qed_scores, nbinsx=10, marker_color='blue'),
                row=1, col=2
            )

            fig.update_layout(
                title='類藥性分析',
                template='plotly_white',
                showlegend=False
            )

            return fig.to_html(include_plotlyjs='cdn')

        except Exception as e:
            logger.error(f"類藥性分析圖創建失敗: {str(e)}")
            return ""

    async def _create_admet_plots(self, molecules: List[Dict]) -> str:
        """創建ADMET預測圖"""
        try:
            # 準備ADMET數據
            admet_data = {
                'BBB穿透': sum(1 for mol in molecules if mol['admet_properties']['bbb_permeant']),
                'P-gp底物': sum(1 for mol in molecules if mol['admet_properties']['pgp_substrate']),
                'Ames致突變': sum(1 for mol in molecules if mol['admet_properties']['ames_mutagenicity']),
                '肝毒性': sum(1 for mol in molecules if mol['admet_properties']['hepatotoxicity'])
            }

            fig = go.Figure(data=[
                go.Bar(
                    x=list(admet_data.keys()),
                    y=list(admet_data.values()),
                    marker_color=['green', 'orange', 'red', 'red']
                )
            ])

            fig.update_layout(
                title='ADMET預測結果',
                yaxis_title='分子數量',
                template='plotly_white'
            )

            return fig.to_html(include_plotlyjs='cdn')

        except Exception as e:
            logger.error(f"ADMET預測圖創建失敗: {str(e)}")
            return ""

# 創建全局實例
molecular_calculator = MolecularPropertyCalculator()
