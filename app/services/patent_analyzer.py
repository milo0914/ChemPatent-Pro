
import re
import spacy
from typing import List, Dict, Optional, Tuple, Set
import numpy as np
from collections import defaultdict, Counter
from datetime import datetime
import json
from loguru import logger

class PatentClaimsAnalyzer:
    """專利權利要求深度分析器"""

    def __init__(self):
        # 嘗試加載spaCy模型
        self.nlp_models = {}
        try:
            self.nlp_models['en'] = spacy.load('en_core_web_sm')
        except OSError:
            logger.warning("英文spaCy模型未安裝")

        try:
            self.nlp_models['zh'] = spacy.load('zh_core_web_sm')
        except OSError:
            logger.warning("中文spaCy模型未安裝")

        # 專利相關關鍵詞
        self.patent_keywords = {
            'claim_indicators': [
                '權利要求', 'claim', 'claims', '請求項',
                '發明內容', 'invention', 'technical field',
                '背景技術', 'background', 'prior art'
            ],
            'technical_terms': [
                '化合物', 'compound', 'molecule', '分子',
                '方法', 'method', 'process', '工藝',
                '組成物', 'composition', 'formulation', '製劑',
                '用途', 'use', 'application', '應用',
                '設備', 'apparatus', 'device', '裝置'
            ],
            'dependency_words': [
                '根據', 'according to', '如', 'as defined in',
                '其中', 'wherein', 'where', '特徵在於',
                '包含', 'comprising', 'including', '含有',
                '由', 'consisting of', 'made of', '構成'
            ]
        }

    async def analyze_patent_claims(self, text: str, language: str = 'auto') -> Dict:
        """
        分析專利權利要求

        Args:
            text: 專利文本內容
            language: 語言代碼 ('zh', 'en', 'auto')

        Returns:
            分析結果字典
        """
        try:
            logger.info(f"開始分析專利權利要求，語言: {language}")

            # 自動檢測語言
            if language == 'auto':
                language = self._detect_language(text)
                logger.info(f"檢測到語言: {language}")

            # 提取權利要求
            claims = await self._extract_claims(text, language)

            # 分析權利要求結構
            claim_structure = await self._analyze_claim_structure(claims, language)

            # 分析依賴關係
            dependencies = await self._analyze_claim_dependencies(claims)

            # 提取技術特徵
            technical_features = await self._extract_technical_features(claims, language)

            # 分析創新點
            innovations = await self._identify_innovations(claims, language)

            # 計算覆蓋範圍
            coverage_analysis = await self._analyze_coverage_scope(claims)

            # 檢測潛在問題
            potential_issues = await self._detect_potential_issues(claims, language)

            # 生成建議
            suggestions = await self._generate_suggestions(claims, potential_issues)

            result = {
                'total_claims': len(claims),
                'language': language,
                'claims': claims,
                'structure_analysis': claim_structure,
                'dependency_tree': dependencies,
                'technical_features': technical_features,
                'innovations': innovations,
                'coverage_scope': coverage_analysis,
                'potential_issues': potential_issues,
                'suggestions': suggestions,
                'analysis_summary': self._generate_summary(claims, technical_features, innovations)
            }

            logger.success(f"專利分析完成，共分析{len(claims)}項權利要求")
            return result

        except Exception as e:
            logger.error(f"專利分析失敗: {str(e)}")
            raise

    async def _extract_claims(self, text: str, language: str) -> List[Dict]:
        """提取權利要求"""
        claims = []

        # 不同語言的權利要求模式
        if language == 'zh':
            patterns = [
                r'權利要求\s*(\d+)[：:](.*?)(?=權利要求\s*\d+|$)',
                r'請求項\s*(\d+)[：:](.*?)(?=請求項\s*\d+|$)',
                r'(\d+)\s*[.、]\s*(.*?)(?=\d+\s*[.、]|$)'
            ]
        else:
            patterns = [
                r'Claim\s*(\d+)[.:](.*?)(?=Claim\s*\d+|$)',
                r'(\d+)\s*\.(.*?)(?=\d+\s*\.|$)'
            ]

        for pattern in patterns:
            matches = re.finditer(pattern, text, re.DOTALL | re.IGNORECASE)
            for match in matches:
                claim_number = int(match.group(1))
                claim_text = match.group(2).strip()

                if len(claim_text) > 10:  # 過濾太短的匹配
                    claims.append({
                        'number': claim_number,
                        'text': claim_text,
                        'type': self._classify_claim_type(claim_text, language),
                        'word_count': len(claim_text.split()),
                        'complexity_score': self._calculate_complexity(claim_text)
                    })

        # 如果沒有找到編號的權利要求，嘗試段落分割
        if not claims:
            paragraphs = re.split(r'\n\s*\n', text)
            for i, para in enumerate(paragraphs):
                if len(para.strip()) > 50 and self._looks_like_claim(para, language):
                    claims.append({
                        'number': i + 1,
                        'text': para.strip(),
                        'type': self._classify_claim_type(para, language),
                        'word_count': len(para.split()),
                        'complexity_score': self._calculate_complexity(para)
                    })

        return sorted(claims, key=lambda x: x['number'])

    def _classify_claim_type(self, claim_text: str, language: str) -> str:
        """分類權利要求類型"""
        claim_lower = claim_text.lower()

        if language == 'zh':
            if any(word in claim_lower for word in ['化合物', '分子', '物質']):
                return 'product'
            elif any(word in claim_lower for word in ['方法', '工藝', '步驟']):
                return 'method'
            elif any(word in claim_lower for word in ['用途', '應用', '治療']):
                return 'use'
            elif any(word in claim_lower for word in ['組成物', '製劑', '配方']):
                return 'composition'
        else:
            if any(word in claim_lower for word in ['compound', 'molecule', 'substance']):
                return 'product'
            elif any(word in claim_lower for word in ['method', 'process', 'step']):
                return 'method'
            elif any(word in claim_lower for word in ['use', 'application', 'treatment']):
                return 'use'
            elif any(word in claim_lower for word in ['composition', 'formulation']):
                return 'composition'

        return 'other'

    def _looks_like_claim(self, text: str, language: str) -> bool:
        """判斷文本是否看起來像權利要求"""
        # 檢查是否包含專利相關關鍵詞
        text_lower = text.lower()

        if language == 'zh':
            keywords = ['包含', '包括', '含有', '特徵在於', '其中']
        else:
            keywords = ['comprising', 'including', 'wherein', 'characterized']

        return any(keyword in text_lower for keyword in keywords)

    def _calculate_complexity(self, text: str) -> float:
        """計算權利要求複雜度"""
        # 基於句子長度、從句數量、術語密度等計算
        words = len(text.split())
        sentences = len(re.split(r'[.!?]', text))
        commas = text.count(',')
        semicolons = text.count(';')
        brackets = text.count('(') + text.count('[')

        complexity = (words / max(sentences, 1)) + commas * 0.1 + semicolons * 0.2 + brackets * 0.15
        return round(complexity, 2)

    async def _analyze_claim_structure(self, claims: List[Dict], language: str) -> Dict:
        """分析權利要求結構"""
        structure = {
            'independent_claims': [],
            'dependent_claims': [],
            'claim_types': Counter(),
            'complexity_distribution': {},
            'length_statistics': {}
        }

        word_counts = []
        complexity_scores = []

        for claim in claims:
            # 判斷獨立/依賴權利要求
            if self._is_dependent_claim(claim['text'], language):
                structure['dependent_claims'].append(claim['number'])
            else:
                structure['independent_claims'].append(claim['number'])

            structure['claim_types'][claim['type']] += 1
            word_counts.append(claim['word_count'])
            complexity_scores.append(claim['complexity_score'])

        # 統計信息
        if word_counts:
            structure['length_statistics'] = {
                'min_words': min(word_counts),
                'max_words': max(word_counts),
                'avg_words': round(sum(word_counts) / len(word_counts), 1),
                'median_words': sorted(word_counts)[len(word_counts)//2]
            }

        if complexity_scores:
            structure['complexity_distribution'] = {
                'min_complexity': min(complexity_scores),
                'max_complexity': max(complexity_scores),
                'avg_complexity': round(sum(complexity_scores) / len(complexity_scores), 2)
            }

        return structure

    def _is_dependent_claim(self, claim_text: str, language: str) -> bool:
        """判斷是否為依賴權利要求"""
        claim_lower = claim_text.lower()

        if language == 'zh':
            dependency_indicators = ['根據權利要求', '如權利要求', '依照權利要求']
        else:
            dependency_indicators = ['according to claim', 'as claimed in', 'of claim']

        return any(indicator in claim_lower for indicator in dependency_indicators)

    async def _analyze_claim_dependencies(self, claims: List[Dict]) -> Dict:
        """分析權利要求依賴關係"""
        dependencies = {
            'tree': {},
            'levels': {},
            'orphaned_claims': [],
            'circular_dependencies': []
        }

        claim_refs = {}

        for claim in claims:
            claim_num = claim['number']
            dependencies['tree'][claim_num] = []

            # 查找依賴的權利要求編號
            ref_pattern = r'權利要求\s*(\d+)|claim\s*(\d+)'
            matches = re.findall(ref_pattern, claim['text'], re.IGNORECASE)

            for match in matches:
                ref_num = int(match[0] or match[1])
                if ref_num != claim_num and ref_num in [c['number'] for c in claims]:
                    dependencies['tree'][claim_num].append(ref_num)
                    claim_refs[claim_num] = claim_refs.get(claim_num, []) + [ref_num]

        # 計算依賴層級
        dependencies['levels'] = self._calculate_dependency_levels(dependencies['tree'])

        # 檢測循環依賴
        dependencies['circular_dependencies'] = self._detect_circular_dependencies(dependencies['tree'])

        return dependencies

    def _calculate_dependency_levels(self, tree: Dict) -> Dict:
        """計算依賴層級"""
        levels = {}

        def get_level(claim_num, visited=None):
            if visited is None:
                visited = set()

            if claim_num in visited:
                return float('inf')  # 循環依賴

            if claim_num in levels:
                return levels[claim_num]

            deps = tree.get(claim_num, [])
            if not deps:
                levels[claim_num] = 0
                return 0

            visited.add(claim_num)
            max_dep_level = max(get_level(dep, visited.copy()) for dep in deps)
            levels[claim_num] = max_dep_level + 1 if max_dep_level != float('inf') else float('inf')

            return levels[claim_num]

        for claim_num in tree:
            get_level(claim_num)

        return levels

    def _detect_circular_dependencies(self, tree: Dict) -> List[List[int]]:
        """檢測循環依賴"""
        visited = set()
        rec_stack = set()
        cycles = []

        def dfs(node, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in tree.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, path.copy())
                elif neighbor in rec_stack:
                    # 找到循環
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])

            rec_stack.remove(node)

        for node in tree:
            if node not in visited:
                dfs(node, [])

        return cycles

    async def _extract_technical_features(self, claims: List[Dict], language: str) -> Dict:
        """提取技術特徵"""
        features = {
            'chemical_entities': [],
            'processes': [],
            'compositions': [],
            'parameters': [],
            'functional_groups': []
        }

        all_text = ' '.join([claim['text'] for claim in claims])

        # 提取化學實體
        chemical_patterns = [
            r'[A-Z][a-z]?\d*(?:[A-Z][a-z]?\d*)*',  # 分子式
            r'\b\w*(?:化合物|compound|molecule)\w*\b',  # 化合物相關
            r'\b\w*(?:基團|group|radical)\w*\b'  # 基團相關
        ]

        for pattern in chemical_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            features['chemical_entities'].extend(matches)

        # 提取工藝參數
        parameter_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:℃|°C|度)',  # 溫度
            r'(\d+(?:\.\d+)?)\s*(?:小時|h|hour)',  # 時間
            r'(\d+(?:\.\d+)?)\s*(?:%|百分比|percent)',  # 百分比
            r'(\d+(?:\.\d+)?)\s*(?:MPa|Pa|壓力)',  # 壓力
        ]

        for pattern in parameter_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            features['parameters'].extend(matches)

        # 使用NLP提取更複雜的特徵
        if language in self.nlp_models:
            nlp = self.nlp_models[language]
            doc = nlp(all_text[:1000000])  # 限制文本長度以提高性能

            # 提取命名實體
            for ent in doc.ents:
                if ent.label_ in ['PRODUCT', 'ORG', 'PERSON']:
                    if ent.label_ == 'PRODUCT':
                        features['chemical_entities'].append(ent.text)

        # 去重並清理
        for key in features:
            features[key] = list(set(filter(None, features[key])))

        return features

    async def _identify_innovations(self, claims: List[Dict], language: str) -> Dict:
        """識別創新點"""
        innovations = {
            'novel_features': [],
            'improvement_claims': [],
            'technical_advantages': [],
            'innovation_score': 0.0
        }

        # 創新關鍵詞
        if language == 'zh':
            innovation_keywords = [
                '新穎', '創新', '改進', '優化', '突破', '首次',
                '顯著', '明顯', '更好', '提高', '增強', '減少'
            ]
            advantage_keywords = [
                '優點', '優勢', '有益效果', '技術效果', '改善', '提升'
            ]
        else:
            innovation_keywords = [
                'novel', 'innovative', 'improved', 'enhanced', 'new',
                'significantly', 'substantially', 'better', 'superior'
            ]
            advantage_keywords = [
                'advantage', 'benefit', 'improvement', 'enhancement', 'effect'
            ]

        innovation_score = 0

        for claim in claims:
            text_lower = claim['text'].lower()

            # 檢測創新特徵
            for keyword in innovation_keywords:
                if keyword in text_lower:
                    innovations['novel_features'].append({
                        'claim': claim['number'],
                        'keyword': keyword,
                        'context': self._extract_context(claim['text'], keyword)
                    })
                    innovation_score += 1

            # 檢測技術優勢
            for keyword in advantage_keywords:
                if keyword in text_lower:
                    innovations['technical_advantages'].append({
                        'claim': claim['number'],
                        'keyword': keyword,
                        'context': self._extract_context(claim['text'], keyword)
                    })
                    innovation_score += 0.5

        innovations['innovation_score'] = round(innovation_score / max(len(claims), 1), 2)

        return innovations

    def _extract_context(self, text: str, keyword: str, window: int = 50) -> str:
        """提取關鍵詞上下文"""
        keyword_pos = text.lower().find(keyword.lower())
        if keyword_pos == -1:
            return ""

        start = max(0, keyword_pos - window)
        end = min(len(text), keyword_pos + len(keyword) + window)

        return text[start:end].strip()

    async def _analyze_coverage_scope(self, claims: List[Dict]) -> Dict:
        """分析覆蓋範圍"""
        scope = {
            'breadth_score': 0.0,
            'depth_score': 0.0,
            'protection_areas': [],
            'potential_gaps': []
        }

        # 計算廣度分數（基於權利要求類型的多樣性）
        claim_types = set(claim['type'] for claim in claims)
        scope['breadth_score'] = len(claim_types) / 4.0  # 假設最多4種類型

        # 計算深度分數（基於依賴權利要求的層次）
        max_complexity = max((claim['complexity_score'] for claim in claims), default=0)
        scope['depth_score'] = min(max_complexity / 20.0, 1.0)  # 標準化到0-1

        # 識別保護領域
        protection_areas = Counter(claim['type'] for claim in claims)
        scope['protection_areas'] = dict(protection_areas)

        return scope

    async def _detect_potential_issues(self, claims: List[Dict], language: str) -> List[Dict]:
        """檢測潛在問題"""
        issues = []

        # 檢查權利要求長度
        for claim in claims:
            if claim['word_count'] > 200:
                issues.append({
                    'type': 'length_warning',
                    'claim': claim['number'],
                    'severity': 'medium',
                    'description': f"權利要求{claim['number']}過長({claim['word_count']}詞)，可能影響清晰度"
                })

        # 檢查複雜度
        for claim in claims:
            if claim['complexity_score'] > 15:
                issues.append({
                    'type': 'complexity_warning',
                    'claim': claim['number'],
                    'severity': 'medium',
                    'description': f"權利要求{claim['number']}複雜度較高({claim['complexity_score']})"
                })

        # 檢查獨立權利要求數量
        independent_count = len([c for c in claims if not self._is_dependent_claim(c['text'], language)])
        if independent_count == 0:
            issues.append({
                'type': 'structure_error',
                'severity': 'high',
                'description': "缺少獨立權利要求"
            })
        elif independent_count > 3:
            issues.append({
                'type': 'structure_warning',
                'severity': 'low',
                'description': f"獨立權利要求過多({independent_count})"
            })

        return issues

    async def _generate_suggestions(self, claims: List[Dict], issues: List[Dict]) -> List[str]:
        """生成改進建議"""
        suggestions = []

        # 基於問題生成建議
        for issue in issues:
            if issue['type'] == 'length_warning':
                suggestions.append(f"考慮將權利要求{issue.get('claim')}拆分為多個更簡潔的權利要求")
            elif issue['type'] == 'complexity_warning':
                suggestions.append(f"簡化權利要求{issue.get('claim')}的語言表達")
            elif issue['type'] == 'structure_error':
                suggestions.append("添加至少一個獨立權利要求作為核心保護")

        # 通用建議
        if len(claims) < 5:
            suggestions.append("考慮增加更多依賴權利要求以擴大保護範圍")

        # 檢查權利要求類型分布
        claim_types = Counter(claim['type'] for claim in claims)
        if len(claim_types) == 1:
            suggestions.append("考慮添加不同類型的權利要求（如方法、用途等）以全面保護發明")

        return list(set(suggestions))

    def _generate_summary(self, claims: List[Dict], features: Dict, innovations: Dict) -> Dict:
        """生成分析摘要"""
        return {
            'total_claims': len(claims),
            'independent_claims': len([c for c in claims if c['type'] != 'dependent']),
            'main_protection_type': Counter(c['type'] for c in claims).most_common(1)[0][0] if claims else 'unknown',
            'innovation_level': 'high' if innovations['innovation_score'] > 0.5 else 'medium' if innovations['innovation_score'] > 0.2 else 'low',
            'technical_complexity': 'high' if any(c['complexity_score'] > 10 for c in claims) else 'medium',
            'key_features_count': len(features['chemical_entities']) + len(features['processes'])
        }

    def _detect_language(self, text: str) -> str:
        """檢測文本語言"""
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        total_chars = len(text)

        if chinese_chars / max(total_chars, 1) > 0.1:
            return 'zh'
        return 'en'

# 創建全局實例
patent_analyzer = PatentClaimsAnalyzer()
