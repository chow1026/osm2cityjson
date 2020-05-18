import copy
import datetime as dt
import json
from pathlib import Path
from sys import platform
from typing import List, Iterable

import fiona
import jsonref
from shapely.geometry import shape
from shapely.geometry.polygon import Polygon

ATTR_KEY_MAPPING = {
        "timestamp": "creationDate",
        "height": "measuredHeight",
        "building:levels": "storeysAboveGround",
        "roof:shape": "roofType",
        "year_of_construction": "yearOfConstruction",
        "year": "yearOfConstruction"
    }

ADDR_KEY_MAPPING = {
    "addr:housename": "ThoroughfareNumber",
    "addr:street": "ThoroughfareName",
    "addr:city": "LocalityName",
    "addr:postcode": "PostalCode",
    "addr:country": "CountryName"
}



## Supposedly you had set up git submodule of cjio set up in cjio folder
## This automatically detect the lastest supported schema versions
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
        all_schemas_dir = Path("cjio/cjio/schemas")
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
        schema_dir = Path(f"cjio/cjio/schemas/{version}")
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


class CityJSONBuilding:
    def __init__(self, geom: Polygon, properties: dict):
        self.properties = properties
        self.geom = geom
        self.height = self._parse_height()
        self.vertices = []
        self.bldg = {
            "type": "Building",
            "attributes": self._parse_attributes(),
            "address": self._parse_address(),
            "geometry": self._parse_geometries_and_surfaces()}

    def get_bldg_object(self):
        return self.bldg

    def get_bldg_height(self):
        return self.height

    def get_bldg_vertices(self):
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
        return attr

    def _parse_height(self) -> float:
        if self.properties["height"] and float(self.properties["height"]) > 0:
            return self.properties["height"]
        else:
            return None

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


class GeoJSON2CityJSON:
    def __init__(self, schema_obj: CityJSONSchema, schema_name: str,
                 geojson_filepath: Path, dest_filepath: Path,
                 metadata: dict = None):
        self.schema_obj = schema_obj
        self.schema = schema_obj.fetch_schema(schema_name)
        self.dest_filepath = dest_filepath
        if self._verify_geojson_filepath(geojson_filepath):
            self.geojson_filepath = geojson_filepath
            # self.features = self._get_geojson_features()
        self.cityjson = {
            "type": "CityJSON",
            "version": self.schema_obj.get_version()}
        if metadata:
            self.cityjson["metadata"] = metadata

    @staticmethod
    def _verify_geojson_filepath(filepath: Path) -> bool:
        return True if filepath.exists() else False

    def _iterate_feature_collection(self) -> Iterable:
        for feature in fiona.open(self.geojson_filepath):
            bldg_id = f"feat_{feature['id']}"
            geom = shape(feature['geometry'])
            attributes = feature['properties']
            bldg = CityJSONBuilding(geom, attributes)
            yield bldg_id, bldg.get_bldg_object(), bldg.get_bldg_vertices()

    def _write_cityjson(self):
        with open(str(self.dest_filepath), 'w') as f:
            json.dump(self.cityjson, f)

    def run(self):
        city_objects = {}
        vertices = []
        for bldg_id, bldg_cityobject, bldg_vertices in self._iterate_feature_collection():
            city_objects.update({bldg_id: bldg_cityobject})
            vertices.append(bldg_vertices)
        self.cityjson["CityObjects"] = city_objects
        self.cityjson["vertices"] = vertices
        self._write_cityjson()


