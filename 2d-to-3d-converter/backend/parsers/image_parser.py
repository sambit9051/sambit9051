"""
Image Parser Module
Extracts geometric information from raster images (PNG, JPEG, etc.)
Uses OpenCV for line detection, contour extraction, and shape recognition
"""

import cv2
import numpy as np
from PIL import Image
import logging
from typing import Dict, List, Any, Tuple

logger = logging.getLogger(__name__)


class ImageParser:
    """Parser for raster image technical drawings"""

    def __init__(self):
        self.min_line_length = 20  # Minimum line length in pixels
        self.max_line_gap = 5      # Maximum gap between line segments
        self.canny_threshold1 = 50
        self.canny_threshold2 = 150

    def parse(self, filepath: str, options: Dict = None) -> Dict:
        """
        Parse image file and extract geometric information

        Args:
            filepath: Path to image file
            options: Parsing options
                - preprocessing: Apply preprocessing (default: True)
                - detect_lines: Detect straight lines (default: True)
                - detect_contours: Detect contours/shapes (default: True)
                - detect_circles: Detect circles (default: True)
                - min_line_length: Minimum line length (default: 20)
                - scale: Pixels per unit (for dimension conversion)

        Returns:
            Dictionary containing:
                - entities: List of geometric entities
                - metadata: Image metadata
                - processed_image: Path to processed image (for debugging)
        """
        options = options or {}

        try:
            # Load image
            img = cv2.imread(filepath)
            if img is None:
                raise ValueError(f"Failed to load image: {filepath}")

            logger.info(f"Loaded image: {filepath}")
            logger.info(f"Size: {img.shape[1]}x{img.shape[0]}")

            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Preprocessing
            if options.get('preprocessing', True):
                gray = self._preprocess_image(gray)

            entities = []

            # Detect lines
            if options.get('detect_lines', True):
                lines = self._detect_lines(gray, options)
                entities.extend(lines)
                logger.info(f"Detected {len(lines)} lines")

            # Detect contours/shapes
            if options.get('detect_contours', True):
                contours = self._detect_contours(gray, options)
                entities.extend(contours)
                logger.info(f"Detected {len(contours)} contours")

            # Detect circles
            if options.get('detect_circles', True):
                circles = self._detect_circles(gray, options)
                entities.extend(circles)
                logger.info(f"Detected {len(circles)} circles")

            # Metadata
            metadata = {
                'filename': filepath.split('/')[-1],
                'width': img.shape[1],
                'height': img.shape[0],
                'channels': img.shape[2] if len(img.shape) > 2 else 1,
                'entity_count': len(entities),
                'scale': options.get('scale', 1.0)  # pixels per unit
            }

            return {
                'entities': entities,
                'metadata': metadata,
                'success': True
            }

        except Exception as e:
            logger.error(f"Image parsing failed: {str(e)}")
            raise

    def _preprocess_image(self, gray: np.ndarray) -> np.ndarray:
        """Preprocess image for better feature detection"""

        # Apply bilateral filter to reduce noise while keeping edges
        denoised = cv2.bilateralFilter(gray, 9, 75, 75)

        # Adaptive thresholding for varying lighting conditions
        thresh = cv2.adaptiveThreshold(
            denoised, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            11, 2
        )

        # Morphological operations to clean up
        kernel = np.ones((3, 3), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        return cleaned

    def _detect_lines(self, gray: np.ndarray, options: Dict) -> List[Dict]:
        """Detect straight lines using Hough Line Transform"""
        lines = []

        try:
            # Edge detection
            edges = cv2.Canny(gray, self.canny_threshold1, self.canny_threshold2)

            # Hough Line Transform
            min_line_length = options.get('min_line_length', self.min_line_length)
            max_line_gap = options.get('max_line_gap', self.max_line_gap)

            detected_lines = cv2.HoughLinesP(
                edges,
                rho=1,
                theta=np.pi/180,
                threshold=50,
                minLineLength=min_line_length,
                maxLineGap=max_line_gap
            )

            if detected_lines is not None:
                for line in detected_lines:
                    x1, y1, x2, y2 = line[0]

                    # Calculate line properties
                    length = np.sqrt((x2-x1)**2 + (y2-y1)**2)
                    angle = np.arctan2(y2-y1, x2-x1) * 180 / np.pi

                    lines.append({
                        'type': 'line',
                        'start': [float(x1), float(y1)],
                        'end': [float(x2), float(y2)],
                        'length': float(length),
                        'angle': float(angle),
                        'layer': 'image_lines',
                        'source': 'opencv'
                    })

        except Exception as e:
            logger.warning(f"Line detection failed: {str(e)}")

        return lines

    def _detect_contours(self, gray: np.ndarray, options: Dict) -> List[Dict]:
        """Detect contours and classify shapes"""
        contours_list = []

        try:
            # Find contours
            contours, hierarchy = cv2.findContours(
                gray,
                cv2.RETR_TREE,
                cv2.CHAIN_APPROX_SIMPLE
            )

            min_area = options.get('min_contour_area', 100)

            for contour in contours:
                area = cv2.contourArea(contour)

                if area < min_area:
                    continue

                # Approximate contour to polygon
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)

                # Extract points
                points = [[float(pt[0][0]), float(pt[0][1])] for pt in approx]

                # Classify shape
                shape_type = self._classify_shape(approx, area)

                # Get bounding box
                x, y, w, h = cv2.boundingRect(contour)

                contour_data = {
                    'type': shape_type,
                    'points': points,
                    'area': float(area),
                    'perimeter': float(cv2.arcLength(contour, True)),
                    'bbox': {
                        'x': float(x),
                        'y': float(y),
                        'width': float(w),
                        'height': float(h)
                    },
                    'layer': 'image_contours',
                    'source': 'opencv'
                }

                # Add specific properties for rectangles
                if shape_type == 'rectangle':
                    contour_data['width'] = float(w)
                    contour_data['height'] = float(h)

                contours_list.append(contour_data)

        except Exception as e:
            logger.warning(f"Contour detection failed: {str(e)}")

        return contours_list

    def _classify_shape(self, approx, area: float) -> str:
        """Classify shape based on number of vertices"""
        vertices = len(approx)

        if vertices == 3:
            return 'triangle'
        elif vertices == 4:
            # Check if it's a square or rectangle
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = w / float(h)
            if 0.95 <= aspect_ratio <= 1.05:
                return 'square'
            else:
                return 'rectangle'
        elif vertices == 5:
            return 'pentagon'
        elif vertices == 6:
            return 'hexagon'
        elif vertices > 6:
            # Check circularity
            perimeter = cv2.arcLength(approx, True)
            circularity = 4 * np.pi * area / (perimeter ** 2)
            if circularity > 0.8:
                return 'circle'
            else:
                return 'polygon'
        else:
            return 'unknown'

    def _detect_circles(self, gray: np.ndarray, options: Dict) -> List[Dict]:
        """Detect circles using Hough Circle Transform"""
        circles = []

        try:
            # Hough Circle Transform
            detected_circles = cv2.HoughCircles(
                gray,
                cv2.HOUGH_GRADIENT,
                dp=1,
                minDist=30,
                param1=self.canny_threshold2,
                param2=30,
                minRadius=options.get('min_circle_radius', 10),
                maxRadius=options.get('max_circle_radius', 0)
            )

            if detected_circles is not None:
                detected_circles = np.uint16(np.around(detected_circles))

                for circle in detected_circles[0, :]:
                    x, y, r = circle

                    circles.append({
                        'type': 'circle',
                        'center': [float(x), float(y)],
                        'radius': float(r),
                        'diameter': float(r * 2),
                        'layer': 'image_circles',
                        'source': 'opencv'
                    })

        except Exception as e:
            logger.warning(f"Circle detection failed: {str(e)}")

        return circles

    def detect_text_regions(self, filepath: str) -> List[Dict]:
        """
        Detect text regions in image (useful for dimension annotations)
        Requires pytesseract
        """
        try:
            import pytesseract

            img = cv2.imread(filepath)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Get bounding boxes for text
            data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)

            text_regions = []
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 60:  # Confidence threshold
                    text_regions.append({
                        'text': data['text'][i],
                        'x': data['left'][i],
                        'y': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i],
                        'confidence': data['conf'][i]
                    })

            return text_regions

        except ImportError:
            logger.warning("pytesseract not installed, text detection unavailable")
            return []
        except Exception as e:
            logger.warning(f"Text detection failed: {str(e)}")
            return []

    def calibrate_scale(self, filepath: str, known_length: float, pixel_length: float) -> float:
        """
        Calibrate scale factor for converting pixels to real-world units

        Args:
            filepath: Image path
            known_length: Known dimension in real units (e.g., 1000mm)
            pixel_length: Length in pixels corresponding to known_length

        Returns:
            Scale factor (units per pixel)
        """
        if pixel_length == 0:
            raise ValueError("pixel_length cannot be zero")

        scale = known_length / pixel_length
        logger.info(f"Calibrated scale: {scale} units/pixel")

        return scale
