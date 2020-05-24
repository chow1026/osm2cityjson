import json
import random
import time
from collections import Iterable
from pathlib import Path
from typing import List

from geojson_rewind import rewind
from shapely.geometry import Point, Polygon, mapping, shape

from cityjson.cityjson import CityJSONSchema, CityObjectTypes, CityJSON, CityObject
from osm.osm import OSM
from util.logging import Logger


class OSM2CityJSON:
    def __init__(self, osm: OSM, logger: Logger, cityjson_path: Path,
                 sample_size: int = 0):
        self.osm = osm
        self.logger = logger
        self.geojson_path = cityjson_path.resolve()
        self.ways = None
        self.nodes = None

    def run(self):
        tic = time.process_time()
        self.ways, self.nodes = self.osm.run()
        city_objects = {}
        vertices = []
        self.convert_to_cityobjects()
        self.write_geojson()
        toc = time.process_time()
        print(f"Conversion to GeoJSON took {toc - tic} seconds.")

    def _get_polygon_geom(self, nd_ids: List) -> List:
        footprint_points = [
            Point(self.nodes[nd_id]["lon"], self.nodes[nd_id]["lat"]) for
            nd_id in nd_ids if nd_id in self.nodes.keys()]

        try:
            polygon = Polygon(footprint_points)
            polygon_geom = shape(mapping(polygon))
            print(polygon_geom)
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
            cityobj = CityObject(cityobject_type, cityobject_geom,
                                    cityobject_properties).get_object()

            cityobject = cityobj.get_object()
            cityobject_vertices = cityobj.get_vertices()
            print(cityobject)
            yield {cityobject_id, cityobject, vertices}

    def convert_to_cityobjects(self):
        for feature in self._iterate_ways():
            # only add feature with valid polygon geometry
            if 'geometry' in feature.keys() and feature['geometry'] is not None:
                self.features.append(self.rewind_geojson(feature))

    def write_geojson(self):
        out_features = self.features    # default to write out all
        if self.sample_size > 0:
            out_features = random.sample(
                population=self.features, k=self.sample_size)
        geojson = GeoJSON(GeoJSONObjectTypes.FeatureCollection,
                          self.geojson_name).get_geojson()
        geojson["features"] = out_features
        print(f"Outputting {len(out_features)} features/buildings.")
        with open(str(self.geojson_path), mode="w") as f:
            json.dump(geojson, f)
