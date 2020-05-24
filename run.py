
from pathlib import Path
from time import process_time
from cityjson.cityjson import CityJSONSchema
from jsonschema import validate
from datetime import datetime as dt

### CityJSON
tik = process_time()
schema_obj = CityJSONSchema("1.0")
metadata = {
    "datasetTitle": "3D Model of OpenStreetMap Buildings in Singapore",
    "datasetReferenceDate": dt.datetime.today().strftime('%Y-%m-%d'),
    "geographicLocation": "Singapore, Republic of Singapore",
    "referenceSystem": "urn:ogc:def:crs:EPSG::3414",
    "geographicalExtent": [
        11474.615816611371,
        28054.808157231186,
        0,
        45326.44585339671,
        48758.78176700817,
        141.3
    ],
    "datasetPointOfContact": {
        "contactName": "NUS Urban Analytics Lab, National University of Singapore",
        "emailAddress": "filip@nus.edu.sg",
        "contactType": "organization",
        "website": "https://ual.sg/"
    },
    "metadataStandard": "ISO 19115 - Geographic Information - Metadata",
    "metadataStandardVersion": "ISO 19115:2014(E)"
    }
# metadata=None
input_geojson = Path("data/singapore-buildings-3414.geojson")
dest_cityjson = Path("data/singapore-buildings.cityjson")
if input_geojson.exists() and input_geojson.is_file():
    cityjson = GeoJSON2CityJSON(schema_obj=schema_obj,
                                schema_name="cityjson",
                                geojson_filepath=input_geojson,
                                dest_filepath=dest_cityjson)
    cityjson.run()
tok = process_time()
print(f"GeoJSON to CityJSON took {tok-tik} seconds.")