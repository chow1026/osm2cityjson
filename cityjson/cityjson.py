import copy
import datetime as dt
import json
from pathlib import Path
from sys import platform
from typing import List, Iterable
from enum import Enum
import fiona
import jsonref
from shapely.geometry import shape
from shapely.geometry.polygon import Polygon


ATTR_KEY_MAPPING = {
        "creationDate": "timestamp",
        "terminationDate": None,
        "class": None,
        "function": None,
        "usage": None,
        "measuredHeight": "height",
        "roofType": "roof:shape",
        "storeysAboveGround": "building:levels",
        "storeysBelowGround": None,
        "storeyHeightsAboveGround": None,
        "storeyHeightsBelowGround": None,
        "yearOfConstruction": "year_of_construction",
        "yearOfDemolition": None}

ADDR_KEY_MAPPING = {
    "ThoroughfareNumber": "addr:housename",
    "ThoroughfareName": "addr:street",
    "LocalityName": "addr:city",
    "PostalCode": "addr:postcode",
    "CountryName": "addr:country"}


class CityJSONSchema:
    def __init__(self, version: str = None):
        self.supported_versions = self._get_supported_schema_versions()
        if version:
            # verify if it is valid version
            if version in self.supported_versions:
                self.version = version
                self.schema_dir = self._validate_schema_folder(version)
            else:
                print(f"Version {version} is an invalid version.")
        else:
            # use the latest version if none specified
            self.version = self.supported_versions[-1]
            self.schema_dir = self._validate_schema_folder(version)
        print(str(self.schema_dir))

    @staticmethod
    def _get_supported_schema_versions() -> List:
        all_schemas_dir = Path("schemas")
        supported_versions = []
        if not all_schemas_dir.exists() or not all_schemas_dir.is_dir():
            raise (f"Schema directory doesn't not exists. Make sure cjio is "
                   f"checked out as submodule.")
        else:
            supported_versions = [child.name for child in
                                  all_schemas_dir.iterdir()]
        return supported_versions

    @staticmethod
    def _validate_schema_folder(version: str) -> Path:
        schema_dir = Path(f"schemas/{version}")
        if schema_dir.exists() and schema_dir.is_dir():
            return schema_dir.resolve()
        else:
            print(f"Schema version {version} doens't exist.")

    def _get_jsonref_base_uri(self) -> str:
        if platform == "darwin" or platform == "linux" or platform == "linux2":
            base_uri = f"file://{str(self.schema_dir)}/"
        else:
            replaced = str(self.schema_dir).replace('\\', '/')
            base_uri = f"file://{replaced}/"
        print(base_uri)
        return base_uri

    def get_version(self) -> str:
        return self.version

    def fetch_schema(self, schema_name: str) -> dict:
        schema_file = Path(
            f"{self.schema_dir}/{schema_name}.schema.json").resolve()
        print(str(schema_file))
        with open(str(schema_file)) as file:
            schema = jsonref.loads(
                file.read(), jsonschema=True,
                base_uri=self._get_jsonref_base_uri())
        return schema


class CityObjectTypes(Enum):
    Building = {
        "type": "Building",
        "attributes": None,     # should be a dict
        "address": None,        # should be a dict
        "geometry": None}       # should be a list
    BuildingPart = {
        "type": "BuildingPart",
        "parent": None,         # should be a list
        "attributes": None,     # should be a dict
        "address": None,        # should be a dict
        "geometry": None}       # should be a list


class CityObject:
    def __init__(self, object_type: Enum, geom: Polygon, properties: dict):
        self.properties = properties
        self.geom = geom
        self.height = self._parse_height()
        self.vertices = []
        self.object = object_type.value

    def get_object(self):
        self.object.update({"attributes": self._parse_attributes()})
        self.object.update({"address": self._parse_address()})
        self.object.update({"geometry": self._parse_geometries_and_surfaces()})
        return self.object

    def get_height(self):
        return self.height

    def get_vertices(self):
        return self.vertices

    def _parse_address(self) -> dict:
        addr = {ADDR_KEY_MAPPING[k]: v for k, v in self.properties.items() if k
                in ADDR_KEY_MAPPING.keys() and v is not None}
        return addr

    def _parse_attributes(self) -> dict:
        attr = {ATTR_KEY_MAPPING[k]: v for k, v in self.properties.items() if k
                in ATTR_KEY_MAPPING.keys() and v is not None}
        attr.update({k: v for k, v in self.properties.items()
                     if k not in ATTR_KEY_MAPPING.keys()})
        if "measuredHeight" in attr.keys():
            attr["measuredHeight"] = float(attr["measuredHeight"])
        return attr

    def _parse_height(self) -> float:
        if self.properties["height"] and float(self.properties["height"]) > 0:
            return float(self.properties["height"])
        else:
            return 10.0

    def _process_ext_ring(self, surfaces: List) -> List:
        ext_ring = list(self.geom.exterior.coords)  # -- exterior ring of each
        # footprint
        ext_ring.pop()  # -- remove last point since first==last
        if not self.geom.exterior.is_ccw:
            # -- to get proper orientation of the normals
            ext_ring.reverse()
        self._extrude_walls(ext_ring, surfaces)
        return ext_ring

    def _process_int_rings(self, surfaces: List) -> List:
        int_rings = [] # -- could be multiple holes, one interior ring for each footprint
        interiors = list(self.geom.interiors)
        for interior in interiors:
            int_ring = list(interior.coords)
            int_ring.pop()  # -- remove last point since first==last
            if interior.is_ccw:
                # -- to get proper orientation of the normals
                int_ring.reverse()
            int_rings.append(int_ring)
            self._extrude_walls(int_ring, surfaces)
        return int_rings

    def _get_top_bottom_surfaces(self, ext_ring: List, int_rings: List,
                                 surfaces: List):
        # -- top-bottom surfaces
        self._extrude_roof_ground(ext_ring, int_rings, self.height, False, surfaces)
        self._extrude_roof_ground(ext_ring, int_rings, 0, True, surfaces)

    def _parse_geometries_and_surfaces(self) -> List:
        # define empty list for geometry
        geometry = []
        geo = {"type": "Solid", "lod": 1.0}

        surfaces = []
        ext_ring = self._process_ext_ring(surfaces)
        int_rings = self._process_int_rings(surfaces)
        self._get_top_bottom_surfaces(ext_ring, int_rings, surfaces)

        # -- add the extruded geometry to the geometry
        geo["boundaries"] = [surfaces]
        # -- add the geom to the building
        geometry.append(geo)
        return geometry

    def _extrude_walls(self, ring: List, surfaces: List):
        #-- each edge become a wall, ie a rectangle
        for (j, v) in enumerate(ring[:-1]):
            self.vertices.append([ring[j][0],   ring[j][1],   0])
            self.vertices.append([ring[j+1][0], ring[j+1][1], 0])
            self.vertices.append([ring[j+1][0], ring[j+1][1], self.height])
            self.vertices.append([ring[j][0],   ring[j][1],   self.height])
            t = len(self.vertices)
            surfaces.append([[t-4, t-3, t-2, t-1]])
        #-- last-first edge
        self.vertices.append([ring[-1][0], ring[-1][1], 0])
        self.vertices.append([ring[0][0],  ring[0][1],  0])
        self.vertices.append([ring[0][0],  ring[0][1],  self.height])
        self.vertices.append([ring[-1][0], ring[-1][1], self.height])
        t = len(self.vertices)
        surfaces.append([[t-4, t-3, t-2, t-1]])

    def _extrude_roof_ground(
            self, ext_ring: List, int_rings: List,
            height: float, reverse:
            bool, surfaces: List):
        ext_ring = copy.deepcopy(ext_ring)
        int_rings = copy.deepcopy(int_rings)
        if reverse:
            ext_ring.reverse()
            for ring in int_rings:
                ring.reverse()
        for (i, pt) in enumerate(ext_ring):
            self.vertices.append([pt[0], pt[1], height])
            ext_ring[i] = (len(self.vertices) - 1)
        for (i, int_ring) in enumerate(int_rings):
            for (j, pt) in enumerate(int_ring):
                self.vertices.append([pt[0], pt[1], height])
                int_rings[i][j] = (len(self.vertices) - 1)
        output = [ext_ring]
        for ring in int_rings:
            output.append(ring)
        surfaces.append(output)


class CityJSON:
    def __init__(self, schema_obj: CityJSONSchema, city_objects: dict,
                 vertices: List, metadata: dict = None):
        self.schema_obj = schema_obj
        self.city_objects = city_objects
        self.vertices = vertices
        self.cityjson = {
            "type": "CityJSON",
            "version": self.schema_obj.get_version(),
            "CityObjects": self.city_objects,
            "vertices": self.vertices}
        if metadata:
            self.cityjson["metadata"] = metadata

    def get_cityjson(self):
        return self.cityjson
