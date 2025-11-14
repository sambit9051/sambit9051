"""
IFC Exporter
Exports 3D models to IFC (Industry Foundation Classes) format
Compatible with: Revit, Tekla, Navisworks, ArchiCAD, etc.
"""

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util
from ifcopenshell.util import element, unit
import numpy as np
import logging
from typing import Dict, List, Any
from datetime import datetime
import uuid as uuid_module

logger = logging.getLogger(__name__)


class IFCExporter:
    """Exporter for IFC format"""

    def __init__(self):
        self.schema = "IFC4"  # or "IFC2X3" for older software

    def export(self, model_data: Dict, filepath: str, options: Dict = None):
        """
        Export 3D model to IFC format

        Args:
            model_data: 3D model data from ModelGenerator
            filepath: Output file path
            options: Export options
                - schema: IFC schema version ("IFC4" or "IFC2X3")
                - project_name: Project name
                - site_name: Site name
                - building_name: Building name
                - author: Author name
                - organization: Organization name
                - units: Length unit ("METRE", "MILLIMETRE", etc.)

        """
        options = options or {}

        schema = options.get('schema', self.schema)
        logger.info(f"Exporting to IFC ({schema}): {filepath}")

        try:
            # Create new IFC file
            ifc_file = ifcopenshell.file(schema=schema)

            # Setup basic IFC structure
            self._create_project_structure(ifc_file, options)

            # Get building storey (where we'll place our elements)
            building_storey = self._get_building_storey(ifc_file)

            # Convert meshes to IFC elements
            meshes = model_data.get('meshes', [])

            for i, mesh_data in enumerate(meshes):
                try:
                    mesh_type = mesh_data.get('type', '')
                    mesh = mesh_data.get('mesh')

                    if mesh is None:
                        continue

                    # Create IFC element based on mesh type
                    if 'polygon' in mesh_type:
                        element = self._create_slab_element(
                            ifc_file, building_storey, mesh, f"Slab_{i}"
                        )
                    elif 'circle' in mesh_type:
                        element = self._create_column_element(
                            ifc_file, building_storey, mesh, f"Column_{i}"
                        )
                    elif 'line' in mesh_type:
                        element = self._create_beam_element(
                            ifc_file, building_storey, mesh, f"Beam_{i}"
                        )
                    else:
                        element = self._create_generic_element(
                            ifc_file, building_storey, mesh, f"Element_{i}"
                        )

                except Exception as e:
                    logger.warning(f"Failed to create IFC element {i}: {str(e)}")

            # Write to file
            ifc_file.write(filepath)

            logger.info(f"IFC export successful: {filepath}")

        except Exception as e:
            logger.error(f"IFC export failed: {str(e)}")
            raise

    def _create_project_structure(self, ifc_file, options: Dict):
        """Create basic IFC project structure"""

        # Create IfcProject
        project_name = options.get('project_name', '2D to 3D Converted Model')
        author = options.get('author', 'Claude AI')
        organization = options.get('organization', 'Anthropic')

        # Owner history
        person = ifc_file.createIfcPerson(
            Identification=author,
            FamilyName=None,
            GivenName=None
        )

        org = ifc_file.createIfcOrganization(
            Identification=None,
            Name=organization
        )

        person_org = ifc_file.createIfcPersonAndOrganization(
            ThePerson=person,
            TheOrganization=org
        )

        application = ifc_file.createIfcApplication(
            ApplicationDeveloper=org,
            Version="1.0",
            ApplicationFullName="2D to 3D Converter",
            ApplicationIdentifier="2d3d"
        )

        timestamp = int(datetime.now().timestamp())

        owner_history = ifc_file.createIfcOwnerHistory(
            OwningUser=person_org,
            OwningApplication=application,
            ChangeAction="ADDED",
            CreationDate=timestamp
        )

        # Create project
        project = ifc_file.createIfcProject(
            GlobalId=self._create_guid(),
            OwnerHistory=owner_history,
            Name=project_name
        )

        # Set units (metric)
        unit_type = options.get('units', 'MILLIMETRE')

        length_unit = ifc_file.createIfcSIUnit(
            UnitType="LENGTHUNIT",
            Name=unit_type
        )

        units = ifc_file.createIfcUnitAssignment(
            Units=[length_unit]
        )

        project.UnitsInContext = units

        # Create site
        site = ifc_file.createIfcSite(
            GlobalId=self._create_guid(),
            OwnerHistory=owner_history,
            Name=options.get('site_name', 'Default Site')
        )

        # Create building
        building = ifc_file.createIfcBuilding(
            GlobalId=self._create_guid(),
            OwnerHistory=owner_history,
            Name=options.get('building_name', 'Default Building')
        )

        # Create building storey
        storey = ifc_file.createIfcBuildingStorey(
            GlobalId=self._create_guid(),
            OwnerHistory=owner_history,
            Name="Level 0",
            Elevation=0.0
        )

        # Create spatial structure
        ifc_file.createIfcRelAggregates(
            GlobalId=self._create_guid(),
            OwnerHistory=owner_history,
            RelatingObject=project,
            RelatedObjects=[site]
        )

        ifc_file.createIfcRelAggregates(
            GlobalId=self._create_guid(),
            OwnerHistory=owner_history,
            RelatingObject=site,
            RelatedObjects=[building]
        )

        ifc_file.createIfcRelAggregates(
            GlobalId=self._create_guid(),
            OwnerHistory=owner_history,
            RelatingObject=building,
            RelatedObjects=[storey]
        )

        # Store owner history for later use
        self.owner_history = owner_history

    def _get_building_storey(self, ifc_file):
        """Get the building storey to place elements in"""
        storeys = ifc_file.by_type("IfcBuildingStorey")
        return storeys[0] if storeys else None

    def _create_slab_element(self, ifc_file, container, mesh, name: str):
        """Create an IfcSlab element"""
        # Create product definition shape from mesh
        shape = self._create_shape_from_mesh(ifc_file, mesh)

        # Create placement (identity for now)
        placement = self._create_local_placement(ifc_file)

        # Create slab
        slab = ifc_file.createIfcSlab(
            GlobalId=self._create_guid(),
            OwnerHistory=self.owner_history,
            Name=name,
            ObjectPlacement=placement,
            Representation=shape,
            PredefinedType="FLOOR"
        )

        # Relate to building storey
        self._relate_to_container(ifc_file, slab, container)

        return slab

    def _create_column_element(self, ifc_file, container, mesh, name: str):
        """Create an IfcColumn element"""
        shape = self._create_shape_from_mesh(ifc_file, mesh)
        placement = self._create_local_placement(ifc_file)

        column = ifc_file.createIfcColumn(
            GlobalId=self._create_guid(),
            OwnerHistory=self.owner_history,
            Name=name,
            ObjectPlacement=placement,
            Representation=shape
        )

        self._relate_to_container(ifc_file, column, container)

        return column

    def _create_beam_element(self, ifc_file, container, mesh, name: str):
        """Create an IfcBeam element"""
        shape = self._create_shape_from_mesh(ifc_file, mesh)
        placement = self._create_local_placement(ifc_file)

        beam = ifc_file.createIfcBeam(
            GlobalId=self._create_guid(),
            OwnerHistory=self.owner_history,
            Name=name,
            ObjectPlacement=placement,
            Representation=shape
        )

        self._relate_to_container(ifc_file, beam, container)

        return beam

    def _create_generic_element(self, ifc_file, container, mesh, name: str):
        """Create a generic IfcBuildingElementProxy"""
        shape = self._create_shape_from_mesh(ifc_file, mesh)
        placement = self._create_local_placement(ifc_file)

        element = ifc_file.createIfcBuildingElementProxy(
            GlobalId=self._create_guid(),
            OwnerHistory=self.owner_history,
            Name=name,
            ObjectPlacement=placement,
            Representation=shape
        )

        self._relate_to_container(ifc_file, element, container)

        return element

    def _create_shape_from_mesh(self, ifc_file, mesh):
        """Create IFC shape representation from trimesh"""
        vertices = mesh.vertices
        faces = mesh.faces

        # Create IFC points
        ifc_points = []
        for v in vertices:
            point = ifc_file.createIfcCartesianPoint(Coordinates=(float(v[0]), float(v[1]), float(v[2])))
            ifc_points.append(point)

        # Create faces
        ifc_faces = []
        for face in faces:
            face_vertices = [ifc_points[i] for i in face]
            poly_loop = ifc_file.createIfcPolyLoop(Polygon=face_vertices)
            face_bound = ifc_file.createIfcFaceOuterBound(Bound=poly_loop, Orientation=True)
            ifc_face = ifc_file.createIfcFace(Bounds=[face_bound])
            ifc_faces.append(ifc_face)

        # Create shell
        shell = ifc_file.createIfcClosedShell(CfsFaces=ifc_faces)

        # Create shape
        rep_item = ifc_file.createIfcFacetedBrep(Outer=shell)

        shape_rep = ifc_file.createIfcShapeRepresentation(
            ContextOfItems=self._get_geometry_context(ifc_file),
            RepresentationIdentifier="Body",
            RepresentationType="Brep",
            Items=[rep_item]
        )

        product_shape = ifc_file.createIfcProductDefinitionShape(
            Representations=[shape_rep]
        )

        return product_shape

    def _get_geometry_context(self, ifc_file):
        """Get or create geometric representation context"""
        contexts = ifc_file.by_type("IfcGeometricRepresentationContext")

        if contexts:
            return contexts[0]

        # Create new context
        context = ifc_file.createIfcGeometricRepresentationContext(
            ContextType="Model",
            CoordinateSpaceDimension=3,
            Precision=1.0E-5,
            WorldCoordinateSystem=self._create_axis_placement_3d(ifc_file)
        )

        return context

    def _create_local_placement(self, ifc_file, relative_to=None):
        """Create local placement"""
        placement = ifc_file.createIfcLocalPlacement(
            PlacementRelTo=relative_to,
            RelativePlacement=self._create_axis_placement_3d(ifc_file)
        )

        return placement

    def _create_axis_placement_3d(self, ifc_file, location=(0., 0., 0.)):
        """Create 3D axis placement (identity)"""
        point = ifc_file.createIfcCartesianPoint(Coordinates=location)

        placement = ifc_file.createIfcAxis2Placement3D(
            Location=point,
            Axis=None,
            RefDirection=None
        )

        return placement

    def _relate_to_container(self, ifc_file, element, container):
        """Relate element to spatial container"""
        if container:
            ifc_file.createIfcRelContainedInSpatialStructure(
                GlobalId=self._create_guid(),
                OwnerHistory=self.owner_history,
                RelatedElements=[element],
                RelatingStructure=container
            )

    def _create_guid(self):
        """Create IFC-compliant GUID"""
        return ifcopenshell.guid.compress(uuid_module.uuid4().hex)
