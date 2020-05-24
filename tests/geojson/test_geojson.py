from geojson.geojson import GeoJSON, GeoJSONObjectTypes

from tests import BaseTest


class TestGeoJSON(BaseTest):
    def setUp(self):
        self._make_test_dir(self.test_output_dir)

    def test_get_feature_geojson(self):
        feature_enum = GeoJSONObjectTypes.Feature
        feature_geojson = GeoJSON(feature_enum, "feature_geojson")
        actual_feature_geojson = feature_geojson.get_geojson()
        expected_feature_geojson = {'type': 'Feature',
                                    'geometry': None,
                                    'properties': None,
                                    'name': 'feature_geojson'}
        self.assertEqual(actual_feature_geojson, expected_feature_geojson)

    def test_get_feature_collection_geojson(self):
        feat_coll_enum = GeoJSONObjectTypes.FeatureCollection
        feat_coll_geojson = GeoJSON(feat_coll_enum,
                                    "feature_collection_geojson")
        actual_feat_coll_geojson = feat_coll_geojson.get_geojson()
        expected_feat_coll_geojson = {'type': 'FeatureCollection',
                                    'features': None,
                                    'name': 'feature_collection_geojson'}
        self.assertEqual(actual_feat_coll_geojson, expected_feat_coll_geojson)

