import json
import time
from collections import Iterable
from pathlib import Path
from typing import List

from shapely.geometry import Point, Polygon, mapping, shape

from cityjson.cityjson import CityJSONSchema, CityObjectTypes, CityJSON, \
    CityObject
from util.logging import Logger


class OSM2CityJSON:
    def __init__(self, ways: dict, nodes: dict, logger: Logger, cityjson_path: Path):
        self.logger = logger
        self.cityjson_path = cityjson_path.resolve()
        self.ways = ways
        self.nodes = nodes

    def run(self):
        tic = time.process_time()
        cityobjects, cityjson_vertices = self.convert_to_cityobjects()
        cityjson = CityJSON(CityJSONSchema(self.logger, '1.0.1'),
                            vertices=cityjson_vertices, city_objects=cityobjects)
        self.write_geojson(cityjson.get_cityjson())
        toc = time.process_time()
        print(f"Conversion to CityJSON took {toc - tic} seconds.")

    def _get_polygon_geom(self, nd_ids: List) -> List:
        footprint_points = [
            Point(self.nodes[nd_id]["lon"], self.nodes[nd_id]["lat"]) for
            nd_id in nd_ids if nd_id in self.nodes.keys()]

        try:
            polygon = Polygon(footprint_points)
            polygon_geom = shape(mapping(polygon))
            # change coordinates from tuple to list
            # footprint['coordinates'] = list(footprint['coordinates'])
            return polygon_geom
        except:
            self.logger.log_error(
                f"Cannot generate to Polygon footprint:"
                f"\n\t{footprint_points}")

    @staticmethod
    def _get_properties(wy_id: str, attrs: dict) -> dict:
        properties = {"osm_id": f"way_{wy_id}"}
        properties.update({k: attrs[k] for k in attrs.keys() if k not in (
            'tags', 'nodes')})
        properties.update(
            {k: attrs["tags"][k] for k in attrs["tags"].keys()})
        return properties


    def _iterate_ways(self) -> Iterable:
        for wy_id, wy in self.ways.items():
            cityobject_type = CityObjectTypes.Building
            cityobject_id = wy_id
            cityobject_properties = self._get_properties(wy_id, wy)
            cityobject_geom = self._get_polygon_geom(wy["nodes"])
            cityobject = CityObject(cityobject_type, cityobject_geom,
                                    cityobject_properties).get_object()
            cityobject_vertices = cityobject["vertices"]
            del cityobject["vertices"]
            yield cityobject_id, cityobject, cityobject_vertices

    def convert_to_cityobjects(self):
        cityobjects = {}
        cityjson_vertices = []
        for cityobject_id, cityobject, cityobject_vertices in self._iterate_ways():
            cityobjects.update({cityobject_id: cityobject})
            cityjson_vertices.extend(cityobject_vertices)
        return cityobjects, cityjson_vertices

    def write_geojson(self, cityjson: dict):
        with open(str(self.cityjson_path), mode="w") as f:
            json.dump(cityjson, f)
