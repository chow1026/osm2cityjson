import json
import random
import time
from collections import Iterable
from pathlib import Path
from typing import List

from geojson_rewind import rewind
from shapely.geometry import Point, Polygon, mapping

from geojson.geojson import GeoJSON, GeoJSONObjectTypes
from util.logging import Logger


class OSM2GeoJSON:
    def __init__(self, ways: dict, nodes: dict, logger: Logger, geojson_path:
    Path, geojson_name: str = None, sample_size: int = 0):
        self.logger = logger
        self.geojson_path = geojson_path.resolve()
        self.sample_size = sample_size
        self.geojson_name = geojson_name
        self.ways = ways
        self.nodes = nodes
        self.features = []

    def run(self):
        tic = time.process_time()
        self.convert_to_features()
        self.write_geojson()
        toc = time.process_time()
        print(f"Conversion to GeoJSON took {toc - tic} seconds.")

    def _get_footprint_geometry(self, nd_ids: List) -> List:
        footprint_points = [
            Point(self.nodes[nd_id]["lon"], self.nodes[nd_id]["lat"]) for
            nd_id in nd_ids if nd_id in self.nodes.keys()]

        try:
            polygon = Polygon(footprint_points)
            footprint = mapping(polygon)
            # change coordinates from tuple to list
            footprint['coordinates'] = list(footprint['coordinates'])
            return footprint
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

    @staticmethod
    def rewind_geojson(geojson: dict) -> List:
        rewound = rewind(geojson)
        return rewound

    def _iterate_ways(self) -> Iterable:
        for wy_id, wy in self.ways.items():
            feature = GeoJSON(GeoJSONObjectTypes.Feature).get_geojson()
            feature.update({'properties': self._get_properties(wy_id, wy)})
            feature.update({'geometry': self._get_footprint_geometry(wy["nodes"])})
            yield feature

    def convert_to_features(self):
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
