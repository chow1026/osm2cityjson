from util.logging import Logger
from pathlib import Path
from time import process_time

from osm2cityjson.osm2cityjson import OSM2CityJSON
from osmnx import OSMContentHandler

from osm.osm import OSM
from shapely.geometry import shape

from cityjson.cityjson import CityJSONSchema, CityObject, CityObjectTypes
from jsonschema import validate
from datetime import datetime as dt

# ### CityJSON
# tik = process_time()
# schema_obj = CityJSONSchema("1.0")
# metadata = {
#     "datasetTitle": "3D Model of OpenStreetMap Buildings in Singapore",
#     "datasetReferenceDate": dt.datetime.today().strftime('%Y-%m-%d'),
#     "geographicLocation": "Singapore, Republic of Singapore",
#     "referenceSystem": "urn:ogc:def:crs:EPSG::3414",
#     "geographicalExtent": [
#         11474.615816611371,
#         28054.808157231186,
#         0,
#         45326.44585339671,
#         48758.78176700817,
#         141.3
#     ],
#     "datasetPointOfContact": {
#         "contactName": "NUS Urban Analytics Lab, National University of Singapore",
#         "emailAddress": "filip@nus.edu.sg",
#         "contactType": "organization",
#         "website": "https://ual.sg/"
#     },
#     "metadataStandard": "ISO 19115 - Geographic Information - Metadata",
#     "metadataStandardVersion": "ISO 19115:2014(E)"
#     }
# # metadata=None
# input_geojson = Path("data/singapore-buildings-3414.geojson")
# dest_cityjson = Path("data/singapore-buildings.cityjson")
# if input_geojson.exists() and input_geojson.is_file():
#     cityjson = GeoJSON2CityJSON(schema_obj=schema_obj,
#                                 schema_name="cityjson",
#                                 geojson_filepath=input_geojson,
#                                 dest_filepath=dest_cityjson)
#     cityjson.run()
# tok = process_time()
# print(f"GeoJSON to CityJSON took {tok-tik} seconds.")
#
# object_type = CityObjectTypes.Building
# geometry = shape({"type": "Polygon", "coordinates": [
#     [[103.763356, 1.3120064], [103.7633559, 1.3119315],
#      [103.7633787, 1.3119315], [103.7633787, 1.3118963],
#      [103.7633955, 1.3118963], [103.7633955, 1.3118686],
#      [103.7636181, 1.3118683], [103.7636181, 1.3118953],
#      [103.763653, 1.3118952], [103.763653, 1.311869],
#      [103.7640596, 1.3118685], [103.764239, 1.3118683],
#      [103.764239, 1.3118963], [103.7642528, 1.3118963],
#      [103.7642528, 1.3119382], [103.7642698, 1.3119382],
#      [103.7642699, 1.3120089], [103.7640261, 1.3120092],
#      [103.7640261, 1.3120209], [103.7639638, 1.312021],
#      [103.7639638, 1.3120101], [103.7639205, 1.3120102],
#      [103.7636271, 1.3120105], [103.7636272, 1.3120273],
#      [103.7636017, 1.3120273], [103.7636017, 1.3120061],
#      [103.763356, 1.3120064]]]})
# properties = {
#     "osm_id": "way_118994826",
#     "type": "way",
#     "version": "4",
#     "timestamp": "2018-05-29T11:50:30Z",
#     "uid": "741163",
#     "user": "JaLooNz",
#     "changeset": "59365536",
#     "addr:city": "Singapore",
#     "addr:country": "SG",
#     "addr:housenumber": "427",
#     "addr:postcode": "120427",
#     "addr:street": "Clementi Avenue 3",
#     "building": "residential",
#     "building:levels": "12",
#     "residential": "HDB",
#     "source": "Bing",
#     "height": "239"
#     }
# city_object = CityObject(object_type=object_type, geometry=geometry, properties=properties)
# city_object.self_construct()
# print(city_object.get_object())
logger = Logger(debug=True)
input_osm_path = Path("tests/fixtures/sample-buildings.osm").resolve()
print(f"input osm path :: {input_osm_path}")
osm_hander = OSMContentHandler()
actual_ways, actual_nodes = OSM(input_osm_path, osm_hander, logger).run()
cityjson_filepath = Path("tests/output/sample-buildings.cityjson").resolve()
