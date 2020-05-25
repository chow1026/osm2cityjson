import json
from pathlib import Path
from datetime import datetime as dt
from shapely.geometry import shape

from cityjson.cityjson import CityObjectTypes, CityJSONSchema, CityObject, \
    CityJSON
from tests import BaseTest
from util.logging import Logger


class TestCityJSONSchema(BaseTest):
    def setUp(self):
        self._make_test_dir(self.test_output_dir)
        self.logger = Logger(debug=True)
        self.schema_obj = CityJSONSchema(self.logger)

    def test__get_supported_schema_versions(self):
        expected_supported_versions = ['0.9', '1.0.0', '1.0.1']
        actual_supported_versions = \
            self.schema_obj._get_supported_schema_versions()
        self.assertEqual(sorted(actual_supported_versions),
                         sorted(expected_supported_versions))

    def test_fetch_schema(self):
        schema_obj = CityJSONSchema(self.logger, "1.0.1")
        actual_schema = schema_obj.fetch_schema("cityjson")
        with open(Path(self.fixture_dir) / "cityjson.1.0.1.schema.json") as f:
            expected_schema = json.load(f)
            self.assertEqual(actual_schema, expected_schema)

    def test_fetch_with_no_version(self):
        schema_obj = CityJSONSchema(self.logger)
        actual_schema = schema_obj.fetch_schema("cityjson")
        with open(Path(self.fixture_dir) / "cityjson.1.0.1.schema.json") as f:
            expected_schema = json.load(f)
            self.assertEqual(actual_schema, expected_schema)


class TestCityObject(BaseTest):
    def setUp(self):
        self._make_test_dir(self.test_output_dir)
        self.object_type = CityObjectTypes.Building
        self.geometry = shape({"type": "Polygon", "coordinates": [
            [[103.763356, 1.3120064], [103.7633559, 1.3119315],
             [103.7633787, 1.3119315], [103.7633787, 1.3118963],
             [103.7633955, 1.3118963], [103.7633955, 1.3118686],
             [103.7636181, 1.3118683], [103.7636181, 1.3118953],
             [103.763653, 1.3118952], [103.763653, 1.311869],
             [103.7640596, 1.3118685], [103.764239, 1.3118683],
             [103.764239, 1.3118963], [103.7642528, 1.3118963],
             [103.7642528, 1.3119382], [103.7642698, 1.3119382],
             [103.7642699, 1.3120089], [103.7640261, 1.3120092],
             [103.7640261, 1.3120209], [103.7639638, 1.312021],
             [103.7639638, 1.3120101], [103.7639205, 1.3120102],
             [103.7636271, 1.3120105], [103.7636272, 1.3120273],
             [103.7636017, 1.3120273], [103.7636017, 1.3120061],
             [103.763356, 1.3120064]]]})
        self.properties = {
            "osm_id": "way_118994826",
            "type": "way",
            "version": "4",
            "timestamp": "2018-05-29T11:50:30Z",
            "uid": "741163",
            "user": "JaLooNz",
            "changeset": "59365536",
            "addr:city": "Singapore",
            "addr:country": "SG",
            "addr:housenumber": "427",
            "addr:postcode": "120427",
            "addr:street": "Clementi Avenue 3",
            "building": "residential",
            "building:levels": "12",
            "residential": "HDB",
            "source": "Bing",
            "height": "239"
            }
        self.city_object = CityObject(
            object_type=self.object_type, geometry=self.geometry,
            properties=self.properties)

    def test__parse_height(self):
        properties = {"osm_id": "way_118994826",
                      "type": "way",
                      "addr:country": "SG"}
        city_object = CityObject(
            object_type=self.object_type, geometry=self.geometry,
            properties=properties)
        self.assertEqual(city_object._parse_height(), float("0.0"))
        properties = {"osm_id": "way_118994826",
                      "type": "way",
                      "height": "239"}
        city_object = CityObject(
            object_type=self.object_type, geometry=self.geometry,
            properties=properties)
        self.assertEqual(city_object._parse_height(), float("239.0"))

    def test__parse_attributes(self):
        actual_attr = self.city_object._parse_attributes()
        expected_attr = {'creationDate': '2018-05-29T11:50:30Z',
                         'storeysAboveGround': '12',
                         'measuredHeight': 239.0,
                         'osm_id': 'way_118994826',
                         'type': 'way',
                         'version': '4',
                         'uid': '741163',
                         'user': 'JaLooNz',
                         'changeset': '59365536',
                         'addr:city': 'Singapore',
                         'addr:country': 'SG',
                         'addr:housenumber': '427',
                         'addr:postcode': '120427',
                         'addr:street': 'Clementi Avenue 3',
                         'building': 'residential',
                         'residential': 'HDB',
                         'source': 'Bing'}
        self.assertEqual(expected_attr, actual_attr)

    def test__parse_address(self):
        actual_addr = self.city_object._parse_address()
        expected_addr = {'LocalityName': 'Singapore',
                         'CountryName': 'SG',
                         'ThoroughfareNumber': '427',
                         'PostalCode': '120427',
                         'ThoroughfareName': 'Clementi Avenue 3'}
        self.assertEqual(expected_addr, actual_addr)

    def test_self_constructed_object(self):
        actual_object = self.city_object.get_object()
        del actual_object["vertices"]
        expected_object = {'type': 'Building',
                           'attributes': {
                               'creationDate': '2018-05-29T11:50:30Z',
                               'storeysAboveGround': '12',
                               'measuredHeight': 239.0,
                               'osm_id': 'way_118994826', 'type': 'way',
                               'version': '4', 'uid': '741163',
                               'user': 'JaLooNz',
                               'changeset': '59365536',
                               'addr:city': 'Singapore',
                               'addr:country': 'SG', 'addr:housenumber': '427',
                               'addr:postcode': '120427',
                               'addr:street': 'Clementi Avenue 3',
                               'building': 'residential', 'residential': 'HDB',
                               'source': 'Bing'},
                           'address': {'LocalityName': 'Singapore',
                                       'CountryName': 'SG',
                                       'ThoroughfareNumber': '427',
                                       'PostalCode': '120427',
                                       'ThoroughfareName': 'Clementi Avenue 3'},
                           'geometry': [{'type': 'Solid', 'lod': 1.2,
                                         'boundaries': [
                                             [[[0, 1, 2, 3]], [[4, 5, 6, 7]],
                                              [[8, 9, 10, 11]],
                                              [[12, 13, 14, 15]],
                                              [[16, 17, 18, 19]],
                                              [[20, 21, 22, 23]],
                                              [[24, 25, 26, 27]],
                                              [[28, 29, 30, 31]],
                                              [[32, 33, 34, 35]],
                                              [[36, 37, 38, 39]],
                                              [[40, 41, 42, 43]],
                                              [[44, 45, 46, 47]],
                                              [[48, 49, 50, 51]],
                                              [[52, 53, 54, 55]],
                                              [[56, 57, 58, 59]],
                                              [[60, 61, 62, 63]],
                                              [[64, 65, 66, 67]],
                                              [[68, 69, 70, 71]],
                                              [[72, 73, 74, 75]],
                                              [[76, 77, 78, 79]],
                                              [[80, 81, 82, 83]],
                                              [[84, 85, 86, 87]],
                                              [[88, 89, 90, 91]],
                                              [[92, 93, 94, 95]],
                                              [[96, 97, 98, 99]],
                                              [[100, 101, 102, 103]], [
                                                  [104, 105, 106, 107, 108, 109,
                                                   110, 111, 112, 113, 114, 115,
                                                   116, 117, 118, 119, 120, 121,
                                                   122, 123, 124, 125, 126, 127,
                                                   128, 129]], [
                                                  [130, 131, 132, 133, 134, 135,
                                                   136, 137, 138, 139, 140, 141,
                                                   142, 143, 144, 145, 146, 147,
                                                   148, 149, 150, 151, 152, 153,
                                                   154, 155]]]]}]}
        self.assertEqual(expected_object, actual_object)

    def test_get_vertices(self):
        actual_vertices = self.city_object.get_object()["vertices"]
        expected_vertices = [[103.763356, 1.3120064, 0],
                             [103.7633559, 1.3119315, 0],
                             [103.7633559, 1.3119315, 239.0],
                             [103.763356, 1.3120064, 239.0],
                             [103.7633559, 1.3119315, 0],
                             [103.7633787, 1.3119315, 0],
                             [103.7633787, 1.3119315, 239.0],
                             [103.7633559, 1.3119315, 239.0],
                             [103.7633787, 1.3119315, 0],
                             [103.7633787, 1.3118963, 0],
                             [103.7633787, 1.3118963, 239.0],
                             [103.7633787, 1.3119315, 239.0],
                             [103.7633787, 1.3118963, 0],
                             [103.7633955, 1.3118963, 0],
                             [103.7633955, 1.3118963, 239.0],
                             [103.7633787, 1.3118963, 239.0],
                             [103.7633955, 1.3118963, 0],
                             [103.7633955, 1.3118686, 0],
                             [103.7633955, 1.3118686, 239.0],
                             [103.7633955, 1.3118963, 239.0],
                             [103.7633955, 1.3118686, 0],
                             [103.7636181, 1.3118683, 0],
                             [103.7636181, 1.3118683, 239.0],
                             [103.7633955, 1.3118686, 239.0],
                             [103.7636181, 1.3118683, 0],
                             [103.7636181, 1.3118953, 0],
                             [103.7636181, 1.3118953, 239.0],
                             [103.7636181, 1.3118683, 239.0],
                             [103.7636181, 1.3118953, 0],
                             [103.763653, 1.3118952, 0],
                             [103.763653, 1.3118952, 239.0],
                             [103.7636181, 1.3118953, 239.0],
                             [103.763653, 1.3118952, 0],
                             [103.763653, 1.311869, 0],
                             [103.763653, 1.311869, 239.0],
                             [103.763653, 1.3118952, 239.0],
                             [103.763653, 1.311869, 0],
                             [103.7640596, 1.3118685, 0],
                             [103.7640596, 1.3118685, 239.0],
                             [103.763653, 1.311869, 239.0],
                             [103.7640596, 1.3118685, 0],
                             [103.764239, 1.3118683, 0],
                             [103.764239, 1.3118683, 239.0],
                             [103.7640596, 1.3118685, 239.0],
                             [103.764239, 1.3118683, 0],
                             [103.764239, 1.3118963, 0],
                             [103.764239, 1.3118963, 239.0],
                             [103.764239, 1.3118683, 239.0],
                             [103.764239, 1.3118963, 0],
                             [103.7642528, 1.3118963, 0],
                             [103.7642528, 1.3118963, 239.0],
                             [103.764239, 1.3118963, 239.0],
                             [103.7642528, 1.3118963, 0],
                             [103.7642528, 1.3119382, 0],
                             [103.7642528, 1.3119382, 239.0],
                             [103.7642528, 1.3118963, 239.0],
                             [103.7642528, 1.3119382, 0],
                             [103.7642698, 1.3119382, 0],
                             [103.7642698, 1.3119382, 239.0],
                             [103.7642528, 1.3119382, 239.0],
                             [103.7642698, 1.3119382, 0],
                             [103.7642699, 1.3120089, 0],
                             [103.7642699, 1.3120089, 239.0],
                             [103.7642698, 1.3119382, 239.0],
                             [103.7642699, 1.3120089, 0],
                             [103.7640261, 1.3120092, 0],
                             [103.7640261, 1.3120092, 239.0],
                             [103.7642699, 1.3120089, 239.0],
                             [103.7640261, 1.3120092, 0],
                             [103.7640261, 1.3120209, 0],
                             [103.7640261, 1.3120209, 239.0],
                             [103.7640261, 1.3120092, 239.0],
                             [103.7640261, 1.3120209, 0],
                             [103.7639638, 1.312021, 0],
                             [103.7639638, 1.312021, 239.0],
                             [103.7640261, 1.3120209, 239.0],
                             [103.7639638, 1.312021, 0],
                             [103.7639638, 1.3120101, 0],
                             [103.7639638, 1.3120101, 239.0],
                             [103.7639638, 1.312021, 239.0],
                             [103.7639638, 1.3120101, 0],
                             [103.7639205, 1.3120102, 0],
                             [103.7639205, 1.3120102, 239.0],
                             [103.7639638, 1.3120101, 239.0],
                             [103.7639205, 1.3120102, 0],
                             [103.7636271, 1.3120105, 0],
                             [103.7636271, 1.3120105, 239.0],
                             [103.7639205, 1.3120102, 239.0],
                             [103.7636271, 1.3120105, 0],
                             [103.7636272, 1.3120273, 0],
                             [103.7636272, 1.3120273, 239.0],
                             [103.7636271, 1.3120105, 239.0],
                             [103.7636272, 1.3120273, 0],
                             [103.7636017, 1.3120273, 0],
                             [103.7636017, 1.3120273, 239.0],
                             [103.7636272, 1.3120273, 239.0],
                             [103.7636017, 1.3120273, 0],
                             [103.7636017, 1.3120061, 0],
                             [103.7636017, 1.3120061, 239.0],
                             [103.7636017, 1.3120273, 239.0],
                             [103.7636017, 1.3120061, 0],
                             [103.763356, 1.3120064, 0],
                             [103.763356, 1.3120064, 239.0],
                             [103.7636017, 1.3120061, 239.0],
                             [103.763356, 1.3120064, 239.0],
                             [103.7633559, 1.3119315, 239.0],
                             [103.7633787, 1.3119315, 239.0],
                             [103.7633787, 1.3118963, 239.0],
                             [103.7633955, 1.3118963, 239.0],
                             [103.7633955, 1.3118686, 239.0],
                             [103.7636181, 1.3118683, 239.0],
                             [103.7636181, 1.3118953, 239.0],
                             [103.763653, 1.3118952, 239.0],
                             [103.763653, 1.311869, 239.0],
                             [103.7640596, 1.3118685, 239.0],
                             [103.764239, 1.3118683, 239.0],
                             [103.764239, 1.3118963, 239.0],
                             [103.7642528, 1.3118963, 239.0],
                             [103.7642528, 1.3119382, 239.0],
                             [103.7642698, 1.3119382, 239.0],
                             [103.7642699, 1.3120089, 239.0],
                             [103.7640261, 1.3120092, 239.0],
                             [103.7640261, 1.3120209, 239.0],
                             [103.7639638, 1.312021, 239.0],
                             [103.7639638, 1.3120101, 239.0],
                             [103.7639205, 1.3120102, 239.0],
                             [103.7636271, 1.3120105, 239.0],
                             [103.7636272, 1.3120273, 239.0],
                             [103.7636017, 1.3120273, 239.0],
                             [103.7636017, 1.3120061, 239.0],
                             [103.7636017, 1.3120061, 0],
                             [103.7636017, 1.3120273, 0],
                             [103.7636272, 1.3120273, 0],
                             [103.7636271, 1.3120105, 0],
                             [103.7639205, 1.3120102, 0],
                             [103.7639638, 1.3120101, 0],
                             [103.7639638, 1.312021, 0],
                             [103.7640261, 1.3120209, 0],
                             [103.7640261, 1.3120092, 0],
                             [103.7642699, 1.3120089, 0],
                             [103.7642698, 1.3119382, 0],
                             [103.7642528, 1.3119382, 0],
                             [103.7642528, 1.3118963, 0],
                             [103.764239, 1.3118963, 0],
                             [103.764239, 1.3118683, 0],
                             [103.7640596, 1.3118685, 0],
                             [103.763653, 1.311869, 0],
                             [103.763653, 1.3118952, 0],
                             [103.7636181, 1.3118953, 0],
                             [103.7636181, 1.3118683, 0],
                             [103.7633955, 1.3118686, 0],
                             [103.7633955, 1.3118963, 0],
                             [103.7633787, 1.3118963, 0],
                             [103.7633787, 1.3119315, 0],
                             [103.7633559, 1.3119315, 0],
                             [103.763356, 1.3120064, 0]]
        self.assertEqual(expected_vertices, actual_vertices)


class TestCityJSON(BaseTest):
    def setUp(self):
        self._make_test_dir(self.test_output_dir)
        self.logger = Logger(debug=True)
        self.schema_obj = CityJSONSchema(self.logger)
        self.metadata = {
            "datasetTitle": "Test CityJSON with Metadata",
            "datasetReferenceDate": dt.today().strftime('%Y-%m-%d')
        }

    # def test_get_cityjson(self):
    #     cityjson = CityJSON()
