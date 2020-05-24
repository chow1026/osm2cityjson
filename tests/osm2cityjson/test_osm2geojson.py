import json
from pathlib import Path

from osm.osm import OSM
from osm.osm_content_handler import OSMContentHandler

from osm2cityjson.osm2geojson import OSM2GeoJSON

from tests import BaseTest


class TestOSM2GeoJSON(BaseTest):
    def setUp(self):
        self._make_test_dir(self.test_output_dir)
        self.input_filepath = self.fixture_dir / "sample-buildings.osm"
        self.handler = OSMContentHandler()
        self.osm = OSM(self.input_filepath, self.handler, self.logger,
                       self.test_output_dir)
        self.geojson_path = self.test_output_dir / "sample-buildings.geojson"
        self.sample_geojson_path = \
            self.test_output_dir / "3-sample-buildings.geojson"

    def test_run(self):
        sample_size = 0     # get all
        osm2geojson = OSM2GeoJSON(self.osm, self.logger,
                                  self.geojson_path, "sample building")
        osm2geojson.run()
        actual_filepath = Path(
            self.test_output_dir / "sample-buildings.geojson").absolute()
        expected_filepath = Path(
            self.fixture_dir / "sample-buildings.geojson").absolute()
        with open(actual_filepath, 'r') as actual_f:
            actual = json.load(actual_f)
            with open(expected_filepath, 'r') as expected_f:
                expected = json.load(expected_f)
                self.assertEqual(actual, expected)

    def test_run_sample(self):
        sample_size = 3
        osm2geojson = OSM2GeoJSON(osm=self.osm, logger=self.logger,
                                  geojson_path=self.sample_geojson_path,
                                  geojson_name="3 sample buildings",
                                  sample_size=sample_size)
        osm2geojson.run()
        actual_filepath = Path(
            self.test_output_dir / "3-sample-buildings.geojson").absolute()
        with open(actual_filepath, 'r') as actual_f:
            actual = json.load(actual_f)
            self.assertEqual(len(actual['features']), 3)

