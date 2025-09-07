
import io
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import pdfplumber
import PyPDF2
from pdf2image import convert_from_bytes
import cv2
import numpy as np
from typing import List, Dict, Optional, Tuple
import re
from loguru import logger

class MultilingualPDFParser:
    """多語言PDF解析器，支持中文、英文、日文"""

    def __init__(self):
        self.supported_languages = {
            'zh': 'chi_sim+chi_tra',  # 中文簡體+繁體
            'en': 'eng',              # 英文
            'ja': 'jpn',              # 日文
            'auto': 'chi_sim+chi_tra+eng+jpn'  # 自動檢測
        }

    async def parse_pdf(self, pdf_content: bytes, language: str = 'auto') -> Dict:
        """
        解析PDF文檔

        Args:
            pdf_content: PDF文件內容（bytes）
            language: 語言代碼 ('zh', 'en', 'ja', 'auto')

        Returns:
            解析結果字典
        """
        try:
            logger.info(f"開始解析PDF，語言設置: {language}")

            # 嘗試多種解析方法
            text_content = await self._extract_text_multi_method(pdf_content, language)

            # 提取元數據
            metadata = await self._extract_metadata(pdf_content)

            # 分析文檔結構
            structure = await self._analyze_document_structure(text_content)

            # 檢測語言
            detected_language = await self._detect_language(text_content)

            result = {
                'text_content': text_content,
                'metadata': metadata,
                'structure': structure,
                'detected_language': detected_language,
                'page_count': len(text_content.get('pages', [])),
                'extraction_method': text_content.get('method', 'unknown')
            }

            logger.success(f"PDF解析完成，共{result['page_count']}頁")
            return result

        except Exception as e:
            logger.error(f"PDF解析失败: {str(e)}")
            raise

    async def _extract_text_multi_method(self, pdf_content: bytes, language: str) -> Dict:
        """使用多種方法提取文本"""
        methods = [
            ('pdfplumber', self._extract_with_pdfplumber),
            ('pymupdf', self._extract_with_pymupdf),
            ('ocr', lambda content, lang: self._extract_with_ocr(content, lang))
        ]

        for method_name, method_func in methods:
            try:
                logger.info(f"嘗試使用{method_name}提取文本")
                if method_name == 'ocr':
                    result = await method_func(pdf_content, language)
                else:
                    result = await method_func(pdf_content)

                if result and result.get('pages'):
                    result['method'] = method_name
                    logger.success(f"使用{method_name}成功提取文本")
                    return result

            except Exception as e:
                logger.warning(f"{method_name}提取失败: {str(e)}")
                continue

        raise Exception("所有文本提取方法都失败")

    async def _extract_with_pdfplumber(self, pdf_content: bytes) -> Dict:
        """使用pdfplumber提取文本"""
        pages = []

        with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text() or ""

                # 提取表格
                tables = []
                for table in page.extract_tables():
                    if table:
                        tables.append(table)

                pages.append({
                    'page_number': i + 1,
                    'text': page_text,
                    'tables': tables,
                    'bbox': page.bbox if hasattr(page, 'bbox') else None
                })

        return {'pages': pages}

    async def _extract_with_pymupdf(self, pdf_content: bytes) -> Dict:
        """使用PyMuPDF提取文本"""
        pages = []

        pdf_doc = fitz.open(stream=pdf_content, filetype="pdf")

        for page_num in range(pdf_doc.page_count):
            page = pdf_doc[page_num]

            # 提取文本
            text = page.get_text()

            # 提取圖像
            images = []
            for img_index, img in enumerate(page.get_images()):
                try:
                    xref = img[0]
                    pix = fitz.Pixmap(pdf_doc, xref)
                    if pix.n - pix.alpha < 4:  # 確保是RGB或灰度圖像
                        img_data = pix.tobytes("png")
                        images.append({
                            'index': img_index,
                            'data': img_data,
                            'bbox': page.get_image_bbox(img)
                        })
                    pix = None
                except Exception as e:
                    logger.warning(f"提取圖像失敗: {str(e)}")

            pages.append({
                'page_number': page_num + 1,
                'text': text,
                'images': images,
                'bbox': page.rect
            })

        pdf_doc.close()
        return {'pages': pages}

    async def _extract_with_ocr(self, pdf_content: bytes, language: str) -> Dict:
        """使用OCR提取文本"""
        pages = []

        # 轉換PDF為圖像
        images = convert_from_bytes(pdf_content, dpi=300)

        lang_code = self.supported_languages.get(language, 'eng')

        for i, image in enumerate(images):
            # 圖像預處理
            processed_image = await self._preprocess_image(image)

            # OCR識別
            try:
                text = pytesseract.image_to_string(
                    processed_image, 
                    lang=lang_code,
                    config='--psm 6'
                )

                # 獲取詳細信息
                data = pytesseract.image_to_data(
                    processed_image, 
                    lang=lang_code, 
                    output_type=pytesseract.Output.DICT
                )

                pages.append({
                    'page_number': i + 1,
                    'text': text,
                    'ocr_data': data,
                    'image_size': image.size
                })

            except Exception as e:
                logger.error(f"OCR識別第{i+1}頁失敗: {str(e)}")
                pages.append({
                    'page_number': i + 1,
                    'text': "",
                    'error': str(e)
                })

        return {'pages': pages}

    async def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """圖像預處理以提高OCR準確性"""
        # 轉換為OpenCV格式
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # 轉為灰度
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

        # 去噪
        denoised = cv2.medianBlur(gray, 3)

        # 二值化
        _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # 形態學操作
        kernel = np.ones((1, 1), np.uint8)
        processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        # 轉回PIL格式
        return Image.fromarray(processed)

    async def _extract_metadata(self, pdf_content: bytes) -> Dict:
        """提取PDF元數據"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
            metadata = pdf_reader.metadata

            return {
                'title': metadata.get('/Title', ''),
                'author': metadata.get('/Author', ''),
                'subject': metadata.get('/Subject', ''),
                'creator': metadata.get('/Creator', ''),
                'producer': metadata.get('/Producer', ''),
                'creation_date': str(metadata.get('/CreationDate', '')),
                'modification_date': str(metadata.get('/ModDate', '')),
                'page_count': len(pdf_reader.pages)
            }
        except Exception as e:
            logger.warning(f"提取元數據失敗: {str(e)}")
            return {}

    async def _analyze_document_structure(self, text_content: Dict) -> Dict:
        """分析文檔結構"""
        structure = {
            'headings': [],
            'sections': [],
            'references': [],
            'figures': [],
            'tables': []
        }

        for page in text_content.get('pages', []):
            text = page.get('text', '')

            # 檢測標題（基於格式和關鍵詞）
            headings = self._detect_headings(text)
            structure['headings'].extend(headings)

            # 檢測段落
            sections = self._detect_sections(text)
            structure['sections'].extend(sections)

            # 檢測參考文獻
            references = self._detect_references(text)
            structure['references'].extend(references)

            # 記錄表格
            if page.get('tables'):
                structure['tables'].extend(page['tables'])

        return structure

    def _detect_headings(self, text: str) -> List[str]:
        """檢測標題"""
        headings = []
        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 檢測數字編號標題
            if re.match(r'^\d+\.?\s+.+', line):
                headings.append(line)
            # 檢測全大寫標題
            elif line.isupper() and len(line) > 5:
                headings.append(line)
            # 檢測特殊格式標題
            elif re.match(r'^[A-Z][^.!?]*$', line) and len(line) < 100:
                headings.append(line)

        return headings

    def _detect_sections(self, text: str) -> List[str]:
        """檢測段落"""
        # 按段落分割
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if len(p.strip()) > 50]

    def _detect_references(self, text: str) -> List[str]:
        """檢測參考文獻"""
        references = []

        # 檢測引用格式
        patterns = [
            r'\[\d+\]',  # [1]
            r'\(\d+\)',  # (1)
            r'\w+\s+et\s+al\.?,?\s+\d{4}',  # Author et al., 2023
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            references.extend(matches)

        return list(set(references))

    async def _detect_language(self, text_content: Dict) -> str:
        """檢測文檔主要語言"""
        full_text = ""
        for page in text_content.get('pages', []):
            full_text += page.get('text', '') + " "

        # 簡單的語言檢測邏輯
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', full_text))
        japanese_chars = len(re.findall(r'[\u3040-\u309f\u30a0-\u30ff]', full_text))
        total_chars = len(full_text)

        if chinese_chars / max(total_chars, 1) > 0.1:
            return 'zh'
        elif japanese_chars / max(total_chars, 1) > 0.1:
            return 'ja'
        else:
            return 'en'

# 創建全局實例
pdf_parser = MultilingualPDFParser()
