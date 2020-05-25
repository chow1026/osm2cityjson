from osm.osm import OSM
from osm.osm_content_handler import OSMContentHandler


from tests import BaseTest


class TestOSM(BaseTest):
    def setUp(self):
        self._make_test_dir(self.test_output_dir)
        self.input_filepath = self.fixture_dir / "sample-buildings.osm"
        self.handler = OSMContentHandler()
        self.osm = OSM(self.input_filepath, self.handler, self.logger)

    def test_run(self):
        actual_ways, actual_nodes = self.osm.run()
        self.assertEqual(len(actual_ways), 17)
        self.assertEqual(len(actual_nodes), 335)

