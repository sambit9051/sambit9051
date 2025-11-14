"""
Geometry Engine
Processes and interprets 2D geometric entities
Prepares data for 3D conversion
"""

import numpy as np
from shapely.geometry import LineString, Polygon, Point, MultiPolygon
from shapely.ops import unary_union, polygonize
import logging
from typing import Dict, List, Any, Tuple

logger = logging.getLogger(__name__)


class GeometryEngine:
    """Engine for processing and interpreting 2D geometry"""

    def __init__(self):
        self.tolerance = 0.001  # Geometric tolerance

    def process(self, entities: List[Dict], params: Dict = None) -> Dict:
        """
        Process 2D entities and prepare for 3D conversion

        Args:
            entities: List of 2D geometric entities
            params: Processing parameters
                - auto_close: Auto-close open polylines (default: True)
                - merge_collinear: Merge collinear lines (default: True)
                - detect_regions: Detect closed regions (default: True)
                - simplify: Simplify geometry (default: True)
                - tolerance: Geometric tolerance (default: 0.001)

        Returns:
            Dictionary containing processed geometry:
                - lines: Individual line segments
                - polylines: Connected line sequences
                - polygons: Closed regions
                - circles: Circle entities
                - points: Point entities
                - groups: Grouped entities by layer/type
        """
        params = params or {}
        self.tolerance = params.get('tolerance', 0.001)

        logger.info(f"Processing {len(entities)} entities")

        # Separate entities by type
        lines = []
        circles = []
        polylines = []
        points = []
        text_annotations = []

        for entity in entities:
            etype = entity.get('type', '').lower()

            if etype == 'line':
                lines.append(entity)
            elif etype in ['circle', 'arc']:
                circles.append(entity)
            elif etype in ['polyline', 'polygon', 'rectangle', 'spline']:
                polylines.append(entity)
            elif etype == 'point':
                points.append(entity)
            elif etype == 'text':
                text_annotations.append(entity)

        # Merge collinear lines if requested
        if params.get('merge_collinear', True) and lines:
            lines = self._merge_collinear_lines(lines)
            logger.info(f"Merged to {len(lines)} lines")

        # Detect closed regions
        polygons = []
        if params.get('detect_regions', True):
            polygons = self._detect_closed_regions(lines + polylines)
            logger.info(f"Detected {len(polygons)} closed regions")

        # Group entities by layer
        groups = self._group_by_layer(entities)

        # Calculate bounding box
        bbox = self._calculate_bounding_box(entities)

        return {
            'lines': lines,
            'polylines': polylines,
            'polygons': polygons,
            'circles': circles,
            'points': points,
            'text': text_annotations,
            'groups': groups,
            'bounding_box': bbox,
            'stats': {
                'total_entities': len(entities),
                'lines': len(lines),
                'polylines': len(polylines),
                'polygons': len(polygons),
                'circles': len(circles),
                'points': len(points)
            }
        }

    def _merge_collinear_lines(self, lines: List[Dict]) -> List[Dict]:
        """Merge collinear and connected line segments"""
        if not lines:
            return []

        merged = []
        used = set()

        for i, line1 in enumerate(lines):
            if i in used:
                continue

            start = line1['start']
            end = line1['end']

            # Try to extend this line by finding connected collinear segments
            changed = True
            while changed:
                changed = False
                for j, line2 in enumerate(lines):
                    if j in used or j == i:
                        continue

                    # Check if lines are collinear and connected
                    if self._are_collinear_and_connected(
                        start, end, line2['start'], line2['end']
                    ):
                        # Extend the line
                        start, end = self._extend_line(start, end, line2['start'], line2['end'])
                        used.add(j)
                        changed = True

            merged.append({
                'type': 'line',
                'start': start,
                'end': end,
                'layer': line1.get('layer', 'default')
            })
            used.add(i)

        return merged

    def _are_collinear_and_connected(self, p1, p2, p3, p4) -> bool:
        """Check if two line segments are collinear and connected"""
        # Convert to numpy arrays
        p1 = np.array(p1[:2])
        p2 = np.array(p2[:2])
        p3 = np.array(p3[:2])
        p4 = np.array(p4[:2])

        # Check if endpoints are connected
        connected = (
            np.linalg.norm(p2 - p3) < self.tolerance or
            np.linalg.norm(p2 - p4) < self.tolerance or
            np.linalg.norm(p1 - p3) < self.tolerance or
            np.linalg.norm(p1 - p4) < self.tolerance
        )

        if not connected:
            return False

        # Check collinearity using cross product
        v1 = p2 - p1
        v2 = p4 - p3

        # Normalize
        v1_norm = np.linalg.norm(v1)
        v2_norm = np.linalg.norm(v2)

        if v1_norm < self.tolerance or v2_norm < self.tolerance:
            return False

        v1 = v1 / v1_norm
        v2 = v2 / v2_norm

        # Check if parallel (cross product near zero)
        cross = abs(v1[0] * v2[1] - v1[1] * v2[0])

        return cross < 0.01  # Small angle threshold

    def _extend_line(self, p1, p2, p3, p4):
        """Extend line by merging with another collinear segment"""
        points = [p1, p2, p3, p4]

        # Find the two points that are farthest apart
        max_dist = 0
        endpoints = [p1, p2]

        for i in range(len(points)):
            for j in range(i+1, len(points)):
                pi = np.array(points[i][:2])
                pj = np.array(points[j][:2])
                dist = np.linalg.norm(pj - pi)

                if dist > max_dist:
                    max_dist = dist
                    endpoints = [points[i], points[j]]

        return endpoints[0], endpoints[1]

    def _detect_closed_regions(self, entities: List[Dict]) -> List[Dict]:
        """Detect closed polygonal regions from line and polyline entities"""
        polygons = []

        try:
            # Convert entities to shapely LineStrings
            lines = []

            for entity in entities:
                etype = entity.get('type', '')

                if etype == 'line':
                    start = entity['start'][:2]
                    end = entity['end'][:2]
                    lines.append(LineString([start, end]))

                elif etype in ['polyline', 'polygon', 'rectangle']:
                    points = [p[:2] for p in entity.get('points', [])]
                    if len(points) >= 2:
                        if entity.get('closed', False) and points[0] != points[-1]:
                            points.append(points[0])
                        lines.append(LineString(points))

            if not lines:
                return []

            # Merge all lines
            merged = unary_union(lines)

            # Find polygons
            polys = list(polygonize(merged))

            # Convert back to our format
            for poly in polys:
                if poly.is_valid and poly.area > self.tolerance:
                    coords = list(poly.exterior.coords)
                    polygons.append({
                        'type': 'polygon',
                        'points': [[float(x), float(y)] for x, y in coords],
                        'area': float(poly.area),
                        'perimeter': float(poly.length),
                        'centroid': [float(poly.centroid.x), float(poly.centroid.y)]
                    })

        except Exception as e:
            logger.warning(f"Region detection failed: {str(e)}")

        return polygons

    def _group_by_layer(self, entities: List[Dict]) -> Dict[str, List[Dict]]:
        """Group entities by layer name"""
        groups = {}

        for entity in entities:
            layer = entity.get('layer', 'default')

            if layer not in groups:
                groups[layer] = []

            groups[layer].append(entity)

        return groups

    def _calculate_bounding_box(self, entities: List[Dict]) -> Dict:
        """Calculate overall bounding box"""
        all_points = []

        for entity in entities:
            etype = entity.get('type', '')

            if etype == 'line':
                all_points.extend([entity['start'][:2], entity['end'][:2]])
            elif etype in ['polyline', 'polygon', 'rectangle']:
                all_points.extend([p[:2] for p in entity.get('points', [])])
            elif etype in ['circle', 'arc']:
                center = entity['center'][:2]
                radius = entity['radius']
                all_points.extend([
                    [center[0] - radius, center[1] - radius],
                    [center[0] + radius, center[1] + radius]
                ])
            elif etype == 'point':
                all_points.append(entity['location'][:2])

        if not all_points:
            return {'min': [0, 0], 'max': [0, 0], 'center': [0, 0], 'size': [0, 0]}

        points_array = np.array(all_points)
        min_pt = points_array.min(axis=0)
        max_pt = points_array.max(axis=0)
        center = (min_pt + max_pt) / 2
        size = max_pt - min_pt

        return {
            'min': min_pt.tolist(),
            'max': max_pt.tolist(),
            'center': center.tolist(),
            'size': size.tolist()
        }

    def classify_structural_elements(self, entities: List[Dict], params: Dict = None) -> Dict:
        """
        Classify entities into structural elements
        (beams, columns, plates, bolts, etc.)

        Args:
            entities: Geometric entities
            params: Classification parameters

        Returns:
            Classified structural elements
        """
        params = params or {}

        beams = []
        columns = []
        plates = []
        bolts = []

        # Simple heuristics for classification
        for entity in entities:
            etype = entity.get('type', '')

            if etype == 'rectangle' or etype == 'polygon':
                points = entity.get('points', [])
                if len(points) == 4:
                    # Calculate aspect ratio
                    p1, p2 = np.array(points[0][:2]), np.array(points[2][:2])
                    width = abs(p2[0] - p1[0])
                    height = abs(p2[1] - p1[1])

                    aspect_ratio = max(width, height) / max(min(width, height), 0.001)

                    if aspect_ratio > 4:  # Long and narrow
                        beams.append(entity)
                    elif aspect_ratio < 1.5:  # Square-ish
                        plates.append(entity)
                    else:
                        columns.append(entity)

            elif etype == 'circle':
                radius = entity.get('radius', 0)
                if radius < 50:  # Small circles likely bolts/holes
                    bolts.append(entity)

        return {
            'beams': beams,
            'columns': columns,
            'plates': plates,
            'bolts': bolts
        }
