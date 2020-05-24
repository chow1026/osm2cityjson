from cityjson.cityjson import CityObject, CityJSON, CityObjectTypes, CityJSONSchema

from tests import BaseTest


class TestGeoJSON(BaseTest):
    def setUp(self):
        self._make_test_dir(self.test_output_dir)
        self.input_filepath = self.fixture_dir / "sample-buildings.osm"

    def test_run(self):
        actual_ways, actual_nodes = self.osm.run()
        self.assertEqual(len(actual_ways), 17)
        self.assertEqual(len(actual_nodes), 335)