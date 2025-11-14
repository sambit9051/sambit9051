"""
DXF/DWG Parser Module
Extracts geometric entities from AutoCAD DXF/DWG files
"""

import ezdxf
from ezdxf.addons.drawing import matplotlib
import logging
from typing import Dict, List, Any
import numpy as np

logger = logging.getLogger(__name__)


class DXFParser:
    """Parser for DXF and DWG files"""

    def __init__(self):
        self.supported_entities = [
            'LINE', 'CIRCLE', 'ARC', 'POLYLINE', 'LWPOLYLINE',
            'SPLINE', 'ELLIPSE', 'POINT', 'TEXT', 'MTEXT',
            'INSERT', 'DIMENSION', 'HATCH', '3DFACE', 'SOLID'
        ]

    def parse(self, filepath: str, options: Dict = None) -> Dict:
        """
        Parse DXF/DWG file and extract entities

        Args:
            filepath: Path to DXF/DWG file
            options: Parsing options
                - layers: List of layer names to include (default: all)
                - entity_types: List of entity types to extract (default: all)
                - extract_dimensions: Extract dimension annotations (default: True)
                - units: Force units (default: auto-detect)

        Returns:
            Dictionary containing:
                - entities: List of geometric entities
                - layers: Layer information
                - metadata: File metadata
                - dimensions: Extracted dimensions
        """
        options = options or {}

        try:
            # Load DXF file (ezdxf also supports DWG with additional tools)
            doc = ezdxf.readfile(filepath)
            msp = doc.modelspace()

            logger.info(f"Loaded DXF: {filepath}")
            logger.info(f"DXF version: {doc.dxfversion}")
            logger.info(f"Units: {doc.units}")

            # Extract entities
            entities = []
            dimensions = []
            layers = set()

            # Get filtering options
            target_layers = options.get('layers', None)
            target_types = options.get('entity_types', self.supported_entities)
            extract_dims = options.get('extract_dimensions', True)

            for entity in msp:
                entity_type = entity.dxftype()
                layer_name = entity.dxf.layer

                # Layer filtering
                if target_layers and layer_name not in target_layers:
                    continue

                # Entity type filtering
                if entity_type not in target_types:
                    continue

                layers.add(layer_name)

                # Extract entity data
                entity_data = self._extract_entity(entity)
                if entity_data:
                    entities.append(entity_data)

                # Extract dimensions
                if extract_dims and entity_type.startswith('DIMENSION'):
                    dim_data = self._extract_dimension(entity)
                    if dim_data:
                        dimensions.append(dim_data)

            # Get metadata
            metadata = {
                'filename': filepath.split('/')[-1],
                'dxf_version': doc.dxfversion,
                'units': str(doc.units),
                'layers': sorted(list(layers)),
                'entity_count': len(entities),
                'dimension_count': len(dimensions)
            }

            # Get bounding box
            if entities:
                all_points = []
                for ent in entities:
                    if 'points' in ent:
                        all_points.extend(ent['points'])
                    elif 'start' in ent and 'end' in ent:
                        all_points.extend([ent['start'], ent['end']])
                    elif 'center' in ent:
                        all_points.append(ent['center'])

                if all_points:
                    points_array = np.array(all_points)
                    metadata['bounds'] = {
                        'min': points_array.min(axis=0).tolist(),
                        'max': points_array.max(axis=0).tolist()
                    }

            logger.info(f"Extracted {len(entities)} entities from {len(layers)} layers")

            return {
                'entities': entities,
                'layers': sorted(list(layers)),
                'metadata': metadata,
                'dimensions': dimensions,
                'success': True
            }

        except Exception as e:
            logger.error(f"DXF parsing failed: {str(e)}")
            raise

    def _extract_entity(self, entity) -> Dict:
        """Extract data from a single DXF entity"""
        entity_type = entity.dxftype()

        try:
            if entity_type == 'LINE':
                return {
                    'type': 'line',
                    'start': [entity.dxf.start.x, entity.dxf.start.y, entity.dxf.start.z],
                    'end': [entity.dxf.end.x, entity.dxf.end.y, entity.dxf.end.z],
                    'layer': entity.dxf.layer,
                    'color': entity.dxf.color
                }

            elif entity_type == 'CIRCLE':
                return {
                    'type': 'circle',
                    'center': [entity.dxf.center.x, entity.dxf.center.y, entity.dxf.center.z],
                    'radius': entity.dxf.radius,
                    'layer': entity.dxf.layer,
                    'color': entity.dxf.color
                }

            elif entity_type == 'ARC':
                return {
                    'type': 'arc',
                    'center': [entity.dxf.center.x, entity.dxf.center.y, entity.dxf.center.z],
                    'radius': entity.dxf.radius,
                    'start_angle': entity.dxf.start_angle,
                    'end_angle': entity.dxf.end_angle,
                    'layer': entity.dxf.layer,
                    'color': entity.dxf.color
                }

            elif entity_type in ['POLYLINE', 'LWPOLYLINE']:
                points = []
                for point in entity.get_points():
                    if len(point) >= 2:
                        points.append([point[0], point[1], point[2] if len(point) > 2 else 0])

                return {
                    'type': 'polyline',
                    'points': points,
                    'closed': entity.is_closed if hasattr(entity, 'is_closed') else False,
                    'layer': entity.dxf.layer,
                    'color': entity.dxf.color
                }

            elif entity_type == 'SPLINE':
                # Sample spline to polyline
                points = []
                for point in entity.flattening(0.01):  # 0.01 = tolerance
                    points.append([point[0], point[1], point[2] if len(point) > 2 else 0])

                return {
                    'type': 'spline',
                    'points': points,
                    'degree': entity.dxf.degree if hasattr(entity.dxf, 'degree') else 3,
                    'layer': entity.dxf.layer,
                    'color': entity.dxf.color
                }

            elif entity_type == 'ELLIPSE':
                return {
                    'type': 'ellipse',
                    'center': [entity.dxf.center.x, entity.dxf.center.y, entity.dxf.center.z],
                    'major_axis': [entity.dxf.major_axis.x, entity.dxf.major_axis.y, entity.dxf.major_axis.z],
                    'ratio': entity.dxf.ratio,
                    'start_param': entity.dxf.start_param,
                    'end_param': entity.dxf.end_param,
                    'layer': entity.dxf.layer,
                    'color': entity.dxf.color
                }

            elif entity_type == 'POINT':
                return {
                    'type': 'point',
                    'location': [entity.dxf.location.x, entity.dxf.location.y, entity.dxf.location.z],
                    'layer': entity.dxf.layer,
                    'color': entity.dxf.color
                }

            elif entity_type in ['TEXT', 'MTEXT']:
                text = entity.dxf.text if hasattr(entity.dxf, 'text') else ""
                insert = entity.dxf.insert if hasattr(entity.dxf, 'insert') else (0, 0, 0)

                return {
                    'type': 'text',
                    'text': text,
                    'position': [insert.x, insert.y, insert.z] if hasattr(insert, 'x') else list(insert),
                    'height': entity.dxf.height if hasattr(entity.dxf, 'height') else 0,
                    'layer': entity.dxf.layer,
                    'color': entity.dxf.color
                }

            elif entity_type == '3DFACE':
                # Extract 3D face vertices
                vertices = []
                for i in range(4):
                    try:
                        vtx = getattr(entity.dxf, f'vtx{i}')
                        vertices.append([vtx.x, vtx.y, vtx.z])
                    except:
                        break

                return {
                    'type': '3dface',
                    'vertices': vertices,
                    'layer': entity.dxf.layer,
                    'color': entity.dxf.color
                }

            elif entity_type == 'INSERT':
                # Block insert (reference)
                return {
                    'type': 'insert',
                    'name': entity.dxf.name,
                    'insert': [entity.dxf.insert.x, entity.dxf.insert.y, entity.dxf.insert.z],
                    'scale': [
                        entity.dxf.xscale if hasattr(entity.dxf, 'xscale') else 1,
                        entity.dxf.yscale if hasattr(entity.dxf, 'yscale') else 1,
                        entity.dxf.zscale if hasattr(entity.dxf, 'zscale') else 1
                    ],
                    'rotation': entity.dxf.rotation if hasattr(entity.dxf, 'rotation') else 0,
                    'layer': entity.dxf.layer,
                    'color': entity.dxf.color
                }

            else:
                # Generic entity
                return {
                    'type': entity_type.lower(),
                    'layer': entity.dxf.layer,
                    'color': entity.dxf.color,
                    'raw': str(entity)
                }

        except Exception as e:
            logger.warning(f"Failed to extract {entity_type}: {str(e)}")
            return None

    def _extract_dimension(self, entity) -> Dict:
        """Extract dimension annotation data"""
        try:
            dim_type = entity.dxftype()

            # Get dimension text/value
            dim_text = entity.dxf.text if hasattr(entity.dxf, 'text') else ""
            actual_measurement = entity.get_measurement() if hasattr(entity, 'get_measurement') else None

            return {
                'type': dim_type.lower(),
                'text': dim_text,
                'measurement': actual_measurement,
                'layer': entity.dxf.layer
            }

        except Exception as e:
            logger.warning(f"Failed to extract dimension: {str(e)}")
            return None

    def get_layer_info(self, doc) -> List[Dict]:
        """Extract information about all layers"""
        layers = []

        for layer in doc.layers:
            layers.append({
                'name': layer.dxf.name,
                'color': layer.dxf.color,
                'linetype': layer.dxf.linetype,
                'on': not layer.is_off(),
                'frozen': layer.is_frozen(),
                'locked': layer.is_locked()
            })

        return layers
