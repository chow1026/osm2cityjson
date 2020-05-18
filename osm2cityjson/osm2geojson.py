import json
import time
import xml.sax
from pathlib import Path, PosixPath
from typing import List
import datetime as dt
from collections import Iterable
from geojson_rewind import rewind
import random

import geopandas as gpd
from shapely.geometry import Point, Polygon, mapping

from osm2cityjson.osm_content_handler import OSMContentHandler


class OSM2GeoJSON:
    def __init__(self, input_filepath: Path, output_dir: Path = None,
                 sample_size: int = 0, skip_osm_parsing: bool = False):
        self.input_filepath = input_filepath
        if output_dir:
            self.output_dir = output_dir
        else:
            self.output_dir = Path("/tmp/osm2geojson/")
        self.sample_size = sample_size
        self.skip_osm_parsing = skip_osm_parsing
        self.features_ndjson = \
            Path(f"{self.output_dir}/singapore-buildings-features.ndjson").resolve()
        self.dest_geojson = \
            Path(f"{self.output_dir}/{self.input_filepath.stem}.geojson").resolve()
        self.handler = OSMContentHandler()
        self.ways = {}
        self.nodes = {}

    def run(self):
        if not self.skip_osm_parsing:
            tic = time.process_time()
            self.parse_xml_content()
            toc = time.process_time()
            print(f"Parsing OSM took {toc-tic} seconds.")
        tic = time.process_time()
        self.convert_to_features()
        toc = time.process_time()
        print(f"Conversion to GeoJSON features took {toc - tic} seconds.")
        tic = time.process_time()
        self.write_geojson()
        toc = time.process_time()
        print(f"Writing to GeoJSON took {toc - tic} seconds.")

    def parse_xml_content(self):
        with open(str(self.input_filepath), mode='rb') as osm:
            xml.sax.parse(osm, self.handler)
            osm_obj_json = Path(
                f"{self.output_dir}/"
                f"{self.input_filepath.stem}-osm.json") \
                .resolve()
            with open(osm_obj_json, mode="w") as f:
                json.dump(self.handler.object, f)
            self.ways = self.handler.object["elements"]["ways"]
            self.nodes = self.handler.object["elements"]["nodes"]

    def _get_footprint_geometry(self, nd_ids: List) -> Polygon:
        footprint_points = [
            Point(self.nodes[nd_id]["lon"], self.nodes[nd_id]["lat"]) for
            nd_id in nd_ids if nd_id in self.nodes.keys()]
        try:
            return Polygon(footprint_points)
        except:
            print(f"Cannot convert to Polygon: {footprint_points}")
            return None

    @staticmethod
    def _get_properties(wy_id: str, attrs: dict) -> dict:
        properties = {"osm_id": f"way_{wy_id}"}
        properties.update({k: attrs[k] for k in attrs.keys() if k not in (
            'tags', 'nodes')})
        properties.update(
            {k: attrs["tags"][k] for k in attrs["tags"].keys()})
        return properties

    def _update_epsg(self, input_file: Path, dest_file: Path):
        pass
        # gdf = gpd.read_file(str(input_file))
        # gdf_dest = gdf.copy()
        # gdf_dest.to_crs(epsg=int(self.epsg))
        # gdf_dest.to_file(dest_file, driver='GeoJSON')

    @staticmethod
    def rewind_geojson(geojson: dict) -> List:
        rewound = rewind(geojson)
        return rewound

    def iterate_ways(self) -> Iterable:
        for wy_id, wy in self.ways.items():
            feature = {"type": "Feature",
                       "osm_id": f"way_{wy_id}"}

            polygon = self._get_footprint_geometry(wy["nodes"])

            if polygon:
                feature["geometry"] = mapping(polygon)
                # need to make it list for rewind (to adhere to right hand rule)
                feature["geometry"]["coordinates"] = list(feature["geometry"]["coordinates"])

            properties = self._get_properties(wy_id, wy)
            if properties != {}:
                feature['properties'] = properties

            if "geometry" in feature.keys():
                yield self.rewind_geojson(feature)

    def convert_to_features(self):
        if len(self.ways) == 0 and len(self.nodes) == 0:
            osm_obj_json = Path(
                f"{self.output_dir}/{self.input_filepath.stem}-osm.json") \
                .resolve()
            with open(osm_obj_json) as json_file:
                data = json.load(json_file)
                self.ways = data["elements"]["ways"]
                self.nodes = data["elements"]["nodes"]
        self.output_features_ndjson()

    def output_features_ndjson(self):
        with open(str(self.features_ndjson), mode="w") as ndjson:
            for feature in self.iterate_ways():
                if 'geometry' in feature.keys() and len(feature['geometry']) > 0:
                    # only add feature when has valid geometry
                    json.dump(feature, ndjson)
                    ndjson.write('\n')

    def write_geojson(self):
        gjson = {"type": "FeatureCollection"}
        with open(str(self.features_ndjson), mode="r") as ndjson:
            features = ndjson.readlines()
            if self.sample_size > 0:
                features = random.sample(
                    population=features, k=self.sample_size)

            gjson["features"] = [json.loads(line) for line in features]
        print(f"There are {len(gjson['features'])} features/buildings.")
        with open(str(self.dest_geojson), mode="w") as geojson:
            json.dump(gjson, geojson)
