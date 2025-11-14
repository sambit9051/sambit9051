"""
PDF Parser Module
Extracts geometric information from PDF technical drawings
"""

import pdfplumber
import PyPDF2
from PIL import Image
import io
import re
import logging
from typing import Dict, List, Any
import numpy as np

logger = logging.getLogger(__name__)


class PDFParser:
    """Parser for PDF technical drawings"""

    def __init__(self):
        self.dimension_patterns = [
            r'(\d+\.?\d*)\s*(?:mm|MM|m|M|cm|CM|ft|FT|in|IN|")',  # Numeric with units
            r'(\d+\.?\d*)\s*[xX×]\s*(\d+\.?\d*)',  # Dimensions like 100x200
            r'R\s*(\d+\.?\d*)',  # Radius
            r'Ø\s*(\d+\.?\d*)',  # Diameter
        ]

    def parse(self, filepath: str, options: Dict = None) -> Dict:
        """
        Parse PDF file and extract geometric information

        Args:
            filepath: Path to PDF file
            options: Parsing options
                - pages: List of page numbers to parse (default: all)
                - extract_text: Extract text annotations (default: True)
                - extract_images: Extract and process embedded images (default: True)
                - extract_vectors: Extract vector graphics (default: True)
                - dpi: Resolution for image extraction (default: 300)

        Returns:
            Dictionary containing:
                - entities: List of geometric entities
                - text: Extracted text and dimensions
                - metadata: File metadata
                - pages: Per-page analysis
        """
        options = options or {}

        try:
            entities = []
            all_text = []
            dimensions = []
            pages_data = []

            # Parse with pdfplumber for detailed extraction
            with pdfplumber.open(filepath) as pdf:
                logger.info(f"Loaded PDF: {filepath}")
                logger.info(f"Pages: {len(pdf.pages)}")

                # Get target pages
                target_pages = options.get('pages', range(len(pdf.pages)))

                for page_num in target_pages:
                    if page_num >= len(pdf.pages):
                        continue

                    page = pdf.pages[page_num]
                    page_data = {
                        'page_number': page_num + 1,
                        'width': float(page.width),
                        'height': float(page.height),
                        'entities': [],
                        'text': [],
                        'dimensions': []
                    }

                    # Extract text
                    if options.get('extract_text', True):
                        text_data = self._extract_text(page)
                        page_data['text'] = text_data
                        all_text.extend(text_data)

                        # Extract dimensions from text
                        page_dims = self._extract_dimensions_from_text(text_data)
                        page_data['dimensions'] = page_dims
                        dimensions.extend(page_dims)

                    # Extract vector graphics (lines, rectangles, curves)
                    if options.get('extract_vectors', True):
                        vector_entities = self._extract_vectors(page)
                        page_data['entities'] = vector_entities
                        entities.extend(vector_entities)

                    # Extract images
                    if options.get('extract_images', True):
                        images = self._extract_images(page, page_num)
                        page_data['images'] = images

                    pages_data.append(page_data)

            # Get metadata
            with open(filepath, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                metadata = {
                    'filename': filepath.split('/')[-1],
                    'num_pages': len(pdf_reader.pages),
                    'author': pdf_reader.metadata.get('/Author', '') if pdf_reader.metadata else '',
                    'title': pdf_reader.metadata.get('/Title', '') if pdf_reader.metadata else '',
                    'subject': pdf_reader.metadata.get('/Subject', '') if pdf_reader.metadata else '',
                    'entity_count': len(entities),
                    'dimension_count': len(dimensions)
                }

            logger.info(f"Extracted {len(entities)} entities and {len(dimensions)} dimensions")

            return {
                'entities': entities,
                'text': all_text,
                'dimensions': dimensions,
                'metadata': metadata,
                'pages': pages_data,
                'success': True
            }

        except Exception as e:
            logger.error(f"PDF parsing failed: {str(e)}")
            raise

    def _extract_text(self, page) -> List[Dict]:
        """Extract text elements with positions"""
        text_data = []

        try:
            # Extract words with bounding boxes
            words = page.extract_words()

            for word in words:
                text_data.append({
                    'text': word['text'],
                    'x0': float(word['x0']),
                    'y0': float(word['y0']),
                    'x1': float(word['x1']),
                    'y1': float(word['y1']),
                    'width': float(word['x1'] - word['x0']),
                    'height': float(word['y1'] - word['y0'])
                })

        except Exception as e:
            logger.warning(f"Text extraction failed: {str(e)}")

        return text_data

    def _extract_dimensions_from_text(self, text_data: List[Dict]) -> List[Dict]:
        """Extract dimension values from text"""
        dimensions = []

        for text_item in text_data:
            text = text_item['text']

            for pattern in self.dimension_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)

                if matches:
                    for match in matches:
                        if isinstance(match, tuple):
                            # Multiple values (e.g., 100x200)
                            dim_value = f"{match[0]}x{match[1]}"
                        else:
                            dim_value = match

                        dimensions.append({
                            'value': dim_value,
                            'text': text,
                            'position': {
                                'x': (text_item['x0'] + text_item['x1']) / 2,
                                'y': (text_item['y0'] + text_item['y1']) / 2
                            },
                            'pattern': pattern
                        })

        return dimensions

    def _extract_vectors(self, page) -> List[Dict]:
        """Extract vector graphics (lines, rectangles, curves)"""
        entities = []

        try:
            # Extract lines
            lines = page.lines
            for line in lines:
                entities.append({
                    'type': 'line',
                    'start': [float(line['x0']), float(line['y0'])],
                    'end': [float(line['x1']), float(line['y1'])],
                    'width': float(line.get('width', 1)),
                    'layer': 'pdf_vectors',
                    'source': 'pdf'
                })

            # Extract rectangles
            rects = page.rects
            for rect in rects:
                x0, y0 = float(rect['x0']), float(rect['y0'])
                x1, y1 = float(rect['x1']), float(rect['y1'])

                # Convert rectangle to polyline
                entities.append({
                    'type': 'rectangle',
                    'points': [
                        [x0, y0],
                        [x1, y0],
                        [x1, y1],
                        [x0, y1]
                    ],
                    'closed': True,
                    'layer': 'pdf_vectors',
                    'source': 'pdf'
                })

            # Extract curves
            curves = page.curves
            for curve in curves:
                if 'pts' in curve:
                    points = [[float(pt[0]), float(pt[1])] for pt in curve['pts']]
                    entities.append({
                        'type': 'curve',
                        'points': points,
                        'layer': 'pdf_vectors',
                        'source': 'pdf'
                    })

        except Exception as e:
            logger.warning(f"Vector extraction failed: {str(e)}")

        return entities

    def _extract_images(self, page, page_num: int) -> List[Dict]:
        """Extract embedded images from PDF page"""
        images = []

        try:
            # Get images from page
            if hasattr(page, 'images'):
                for img_idx, img in enumerate(page.images):
                    images.append({
                        'page': page_num + 1,
                        'index': img_idx,
                        'x0': float(img['x0']),
                        'y0': float(img['y0']),
                        'x1': float(img['x1']),
                        'y1': float(img['y1']),
                        'width': float(img['width']),
                        'height': float(img['height'])
                    })

        except Exception as e:
            logger.warning(f"Image extraction failed: {str(e)}")

        return images

    def extract_tables(self, filepath: str) -> List[Dict]:
        """Extract tables from PDF (useful for specs/schedules)"""
        tables = []

        try:
            with pdfplumber.open(filepath) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_tables = page.extract_tables()

                    for table_idx, table in enumerate(page_tables):
                        tables.append({
                            'page': page_num + 1,
                            'index': table_idx,
                            'data': table,
                            'rows': len(table),
                            'cols': len(table[0]) if table else 0
                        })

        except Exception as e:
            logger.warning(f"Table extraction failed: {str(e)}")

        return tables

    def detect_drawing_type(self, text_data: List[Dict]) -> str:
        """
        Detect type of drawing from text content
        (plan, elevation, section, detail, etc.)
        """
        all_text = ' '.join([item['text'] for item in text_data]).upper()

        if 'PLAN' in all_text or 'FLOOR PLAN' in all_text:
            return 'plan'
        elif 'ELEVATION' in all_text:
            return 'elevation'
        elif 'SECTION' in all_text:
            return 'section'
        elif 'DETAIL' in all_text:
            return 'detail'
        elif 'ISOMETRIC' in all_text or 'ISO' in all_text:
            return 'isometric'
        else:
            return 'unknown'
