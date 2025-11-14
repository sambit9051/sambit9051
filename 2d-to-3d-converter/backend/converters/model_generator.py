"""
3D Model Generator
Converts 2D geometry to 3D models using extrusion and other techniques
"""

import numpy as np
import trimesh
import logging
from typing import Dict, List, Any, Tuple
import uuid

logger = logging.getLogger(__name__)


class ModelGenerator:
    """Generator for 3D models from 2D geometry"""

    def __init__(self):
        self.default_extrusion_height = 100.0
        self.default_thickness = 10.0

    def generate(self, geometry: Dict, params: Dict = None) -> Dict:
        """
        Generate 3D model from processed 2D geometry

        Args:
            geometry: Processed geometry from GeometryEngine
            params: Generation parameters
                - extrusion_height: Default extrusion height (default: 100)
                - extrusion_mode: 'uniform' or 'custom' (default: 'uniform')
                - custom_heights: Dict mapping entity indices to heights
                - thickness: Wall/plate thickness (default: 10)
                - generate_solids: Create solid models (default: True)
                - generate_surfaces: Create surface models (default: False)

        Returns:
            Dictionary containing:
                - model_id: Unique model identifier
                - meshes: List of 3D meshes
                - vertices: Combined vertex array
                - faces: Combined face array
                - metadata: Model metadata
                - stats: Model statistics
        """
        params = params or {}

        model_id = str(uuid.uuid4())

        extrusion_height = params.get('extrusion_height', self.default_extrusion_height)
        thickness = params.get('thickness', self.default_thickness)

        logger.info(f"Generating 3D model (height={extrusion_height}, thickness={thickness})")

        meshes = []
        all_vertices = []
        all_faces = []
        vertex_offset = 0

        # Process polygons (extrude to create solids)
        polygons = geometry.get('polygons', [])
        for i, polygon in enumerate(polygons):
            try:
                height = self._get_custom_height(i, params, extrusion_height)
                mesh = self._extrude_polygon(polygon, height)

                if mesh:
                    meshes.append({
                        'type': 'polygon_extrusion',
                        'index': i,
                        'mesh': mesh,
                        'height': height
                    })

                    # Add to combined arrays
                    vertices = mesh.vertices
                    faces = mesh.faces + vertex_offset

                    all_vertices.extend(vertices.tolist())
                    all_faces.extend(faces.tolist())
                    vertex_offset += len(vertices)

            except Exception as e:
                logger.warning(f"Failed to extrude polygon {i}: {str(e)}")

        # Process circles (extrude to create cylinders)
        circles = geometry.get('circles', [])
        for i, circle in enumerate(circles):
            try:
                height = self._get_custom_height(f"circle_{i}", params, extrusion_height)
                mesh = self._extrude_circle(circle, height)

                if mesh:
                    meshes.append({
                        'type': 'circle_extrusion',
                        'index': i,
                        'mesh': mesh,
                        'height': height
                    })

                    vertices = mesh.vertices
                    faces = mesh.faces + vertex_offset

                    all_vertices.extend(vertices.tolist())
                    all_faces.extend(faces.tolist())
                    vertex_offset += len(vertices)

            except Exception as e:
                logger.warning(f"Failed to extrude circle {i}: {str(e)}")

        # Process lines (extrude to create beams/plates)
        lines = geometry.get('lines', [])
        for i, line in enumerate(lines):
            try:
                mesh = self._extrude_line_to_beam(line, thickness, extrusion_height)

                if mesh:
                    meshes.append({
                        'type': 'line_extrusion',
                        'index': i,
                        'mesh': mesh
                    })

                    vertices = mesh.vertices
                    faces = mesh.faces + vertex_offset

                    all_vertices.extend(vertices.tolist())
                    all_faces.extend(faces.tolist())
                    vertex_offset += len(vertices)

            except Exception as e:
                logger.warning(f"Failed to extrude line {i}: {str(e)}")

        # Calculate model statistics
        stats = {
            'total_meshes': len(meshes),
            'total_vertices': len(all_vertices),
            'total_faces': len(all_faces),
            'polygon_extrusions': len(polygons),
            'circle_extrusions': len(circles),
            'line_extrusions': len(lines)
        }

        # Calculate bounding box
        if all_vertices:
            vertices_array = np.array(all_vertices)
            bbox_min = vertices_array.min(axis=0)
            bbox_max = vertices_array.max(axis=0)
            bbox_center = (bbox_min + bbox_max) / 2
            bbox_size = bbox_max - bbox_min

            stats['bounding_box'] = {
                'min': bbox_min.tolist(),
                'max': bbox_max.tolist(),
                'center': bbox_center.tolist(),
                'size': bbox_size.tolist()
            }

        logger.info(f"Generated 3D model: {stats['total_meshes']} meshes, "
                   f"{stats['total_vertices']} vertices, {stats['total_faces']} faces")

        return {
            'model_id': model_id,
            'meshes': meshes,
            'vertices': all_vertices,
            'faces': all_faces,
            'metadata': {
                'extrusion_height': extrusion_height,
                'thickness': thickness,
                'source_geometry': {
                    'polygons': len(polygons),
                    'circles': len(circles),
                    'lines': len(lines)
                }
            },
            'stats': stats,
            'success': True
        }

    def _get_custom_height(self, index, params: Dict, default: float) -> float:
        """Get custom extrusion height for specific entity"""
        custom_heights = params.get('custom_heights', {})
        return custom_heights.get(str(index), default)

    def _extrude_polygon(self, polygon: Dict, height: float) -> trimesh.Trimesh:
        """Extrude a 2D polygon to create a 3D solid"""
        points = polygon.get('points', [])

        if len(points) < 3:
            return None

        # Convert to 3D points (z=0 for bottom, z=height for top)
        points_2d = np.array([[p[0], p[1]] for p in points])

        # Create extruded mesh
        try:
            # Create path for extrusion
            path = trimesh.path.Path2D(entities=[
                trimesh.path.entities.Line(np.arange(len(points_2d)))
            ], vertices=points_2d)

            # Extrude
            mesh = trimesh.creation.extrude_polygon(path, height=height)

            return mesh

        except Exception as e:
            logger.warning(f"Extrusion failed, using fallback method: {str(e)}")

            # Fallback: manual extrusion
            n = len(points_2d)
            vertices = []
            faces = []

            # Bottom vertices
            for p in points_2d:
                vertices.append([p[0], p[1], 0])

            # Top vertices
            for p in points_2d:
                vertices.append([p[0], p[1], height])

            # Bottom face (triangulate)
            for i in range(1, n - 1):
                faces.append([0, i, i + 1])

            # Top face (triangulate)
            for i in range(1, n - 1):
                faces.append([n, n + i + 1, n + i])

            # Side faces
            for i in range(n):
                next_i = (i + 1) % n
                # Two triangles per side face
                faces.append([i, next_i, n + i])
                faces.append([next_i, n + next_i, n + i])

            vertices = np.array(vertices)
            faces = np.array(faces)

            return trimesh.Trimesh(vertices=vertices, faces=faces)

    def _extrude_circle(self, circle: Dict, height: float, segments: int = 32) -> trimesh.Trimesh:
        """Extrude a circle to create a cylinder"""
        center = circle.get('center', [0, 0])
        radius = circle.get('radius', 1.0)

        try:
            # Create cylinder
            mesh = trimesh.creation.cylinder(
                radius=radius,
                height=height,
                sections=segments
            )

            # Translate to correct position
            translation = [center[0], center[1], height / 2]
            mesh.apply_translation(translation)

            return mesh

        except Exception as e:
            logger.warning(f"Cylinder creation failed: {str(e)}")
            return None

    def _extrude_line_to_beam(self, line: Dict, thickness: float, height: float) -> trimesh.Trimesh:
        """
        Extrude a line to create a rectangular beam
        Creates a rectangular profile perpendicular to the line
        """
        start = np.array(line['start'][:2])
        end = np.array(line['end'][:2])

        # Calculate direction vector
        direction = end - start
        length = np.linalg.norm(direction)

        if length < 0.001:
            return None

        direction = direction / length

        # Perpendicular vector (rotate 90 degrees)
        perpendicular = np.array([-direction[1], direction[0]])

        # Create rectangle profile
        half_thickness = thickness / 2

        # Four corners of the rectangle
        p1 = start + perpendicular * half_thickness
        p2 = start - perpendicular * half_thickness
        p3 = end - perpendicular * half_thickness
        p4 = end + perpendicular * half_thickness

        # Create 3D vertices (bottom and top)
        vertices = []
        # Bottom face
        vertices.extend([
            [p1[0], p1[1], 0],
            [p2[0], p2[1], 0],
            [p3[0], p3[1], 0],
            [p4[0], p4[1], 0]
        ])
        # Top face
        vertices.extend([
            [p1[0], p1[1], height],
            [p2[0], p2[1], height],
            [p3[0], p3[1], height],
            [p4[0], p4[1], height]
        ])

        # Create faces
        faces = [
            # Bottom
            [0, 1, 2], [0, 2, 3],
            # Top
            [4, 6, 5], [4, 7, 6],
            # Sides
            [0, 4, 5], [0, 5, 1],
            [1, 5, 6], [1, 6, 2],
            [2, 6, 7], [2, 7, 3],
            [3, 7, 4], [3, 4, 0]
        ]

        vertices = np.array(vertices)
        faces = np.array(faces)

        return trimesh.Trimesh(vertices=vertices, faces=faces)

    def export_obj(self, model_data: Dict, filepath: str):
        """Export model to OBJ format"""
        vertices = model_data.get('vertices', [])
        faces = model_data.get('faces', [])

        with open(filepath, 'w') as f:
            f.write("# Generated by 2D to 3D Converter\n")

            # Write vertices
            for v in vertices:
                f.write(f"v {v[0]} {v[1]} {v[2]}\n")

            # Write faces (1-indexed)
            for face in faces:
                indices = ' '.join([str(i+1) for i in face])
                f.write(f"f {indices}\n")

        logger.info(f"Exported OBJ to {filepath}")

    def export_stl(self, model_data: Dict, filepath: str, binary: bool = True):
        """Export model to STL format"""
        vertices = np.array(model_data.get('vertices', []))
        faces = np.array(model_data.get('faces', []))

        mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

        # Export using trimesh
        mesh.export(filepath, file_type='stl')

        logger.info(f"Exported STL to {filepath}")
