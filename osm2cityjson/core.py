import json
import time
import xml.sax
from pathlib import Path
from typing import List

import geopandas as gpd
from shapely.geometry import Point, Polygon, mapping

from osm2cityjson.osm_content_handler import OSMContentHandler


class OSM2GeoJSON:
    def __init__(self, input_filepath: Path, output_intermediate: bool = True,
                 intermediate_dir: Path = None):
        self.input_filepath = input_filepath
        self.output_intermediate = output_intermediate
        self.intermediate_dir = intermediate_dir
        self.handler = OSMContentHandler()
        self.geojson = {
            "type": "FeatureCollection",
            "crs": {"type": "name",
                    "properties": {"name": "urn:ogc:def:crs:EPSG::4326"}},
            "features": []}
        self.ways = {}
        self.nodes = {}

    def run(self):
        tic = time.process_time()
        self.parse_xml_content()
        toc = time.process_time()
        print(f"Parsing OSM took {toc-tic} seconds.")
        time.sleep(5.0)
        tic = time.process_time()
        self.convert_to_geojson()
        toc = time.process_time()
        print(f"Conversion to GeoJSON took {toc - tic} seconds.")
        print(f"GeoJSON has a total of "
              f"{len(self.geojson['features'])} features.")
        tic = time.process_time()
        dest_file = Path(f"{self.intermediate_dir}/"
                         f"{self.input_filepath.stem}-"
                         f"4326.geojson").resolve()
        self.write_geojson(dest_file)
        toc = time.process_time()
        print(f"Writing to GeoJSON took {toc - tic} seconds.")

    def parse_xml_content(self):
        with open(str(self.input_filepath), mode='rb') as osm:
            xml.sax.parse(osm, self.handler)
            if self.output_intermediate:
                osm_obj_json = Path(
                    f"{self.intermediate_dir}/"
                    f"{self.input_filepath.stem}-obj.json") \
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
    def _get_properties(attrs: dict) -> dict:
        properties = {}
        properties.update({k: attrs[k] for k in attrs.keys() if k not in (
            'tags', 'nodes')})
        properties.update(
            {k: attrs["tags"][k] for k in attrs["tags"].keys()})
        return properties

    def _update_epsg(self, input_file: Path, dest_file: Path):
        gdf = gpd.read_file(str(input_file))
        gdf_dest = gdf.copy()
        gdf_dest.to_crs(epsg=int(self.epsg))
        gdf_dest.to_file(dest_file, driver='GeoJSON')

    def convert_to_geojson(self):
        if len(self.ways) == 0 and len(self.nodes) == 0:
            osm_obj_json = Path(
                f"{self.intermediate_dir}/{self.input_filepath.stem}-obj.json") \
                .resolve()
            with open(osm_obj_json) as json_file:
                data = json.load(json_file)
                self.ways = data["elements"]["ways"]
                self.nodes = data["elements"]["nodes"]

        for wy_id, wy in self.ways.items():
            feature = {"type": "Feature",
                       "osm_id": f"way/{wy_id}",
                       "properties": {}}

            polygon = self._get_footprint_geometry(wy["nodes"])

            if polygon:
                feature["geometry"] = mapping(polygon)

            properties = self._get_properties(wy)
            if properties != {}:
                feature['properties'] = properties

            if 'geometry' in feature.keys() and len(feature['geometry']) > 0:
                # only add feature when has valid geometry
                self.geojson["features"].append(feature)

    def write_geojson(self, dest_file: Path):
        with open(str(dest_file), mode="w") as f:
            json.dump(self.geojson, f)

