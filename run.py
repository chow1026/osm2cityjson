from osm2cityjson.osm2geojson import OSM2GeoJSON
from pathlib import Path
from time import process_time
from osm2cityjson.cityjson import CityJSONSchema, GeoJSON2CityJSON
import subprocess
import datetime as dt
import sys

### OSM2GeoJSON footprints
# set output directory
output_dir = Path("data")
# to verify intermediate file parsing, file name automatically generated
output_intermediate = True
input_filepath = Path("data/singapore-buildings.osm")
osm_json_filepath = Path(f"{output_dir}/{input_filepath.stem}-osm.json")
# skip osm parsing to json if already done before
skip_osm_parsing = True if osm_json_filepath.exists() and \
        osm_json_filepath.is_file() else False
# set 0 if generate full dataset
sample_size = 1000
tik = process_time()
OSM2GeoJSON(input_filepath=input_filepath,
            output_dir=output_dir,
            sample_size=sample_size,
            skip_osm_parsing=skip_osm_parsing).run()
tok = process_time()
print(f"OSM2GeoJSON process took {tok-tik} seconds.")


### Change GeoJSON CRS from default 4326 to 3414 (Singapore)

format = "GEOJSON"
in_geojson = "data/singapore-buildings.geojson"
out_geojson = "data/singapore-buildings-3414.geojson"
in_epsg = "EPSG:4326"
out_epsg = "EPSG:3414"
tik = process_time()
cmd = f"ogr2ogr -f {format} -lco RFC7946=YES " \
      f"{out_geojson} {in_geojson} " \
      f"-s_srs {in_epsg} -t_srs {out_epsg}"
p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
tok = process_time()
print(f"ogr2ogr process took {tok-tik} seconds.")

### CityJSON
tik = process_time()
schema_obj = CityJSONSchema("1.0.1")
metadata = {
    "datasetTitle": "3D Model of OpenStreetMap Buildings in Singapore",
    "datasetReferenceDate": dt.datetime.today().strftime('%Y-$m-%d'),
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
input_geojson = Path("data/singapore-buildings-3414.geojson")
dest_cityjson = Path("data/singapore-buildings.cityjson")
if input_geojson.exists() and input_geojson.is_file():
    cityjson = GeoJSON2CityJSON(schema_obj=schema_obj,
                                schema_name="cityjson",
                                geojson_filepath=input_geojson,
                                dest_filepath=dest_cityjson,
                                metadata=metadata)
    cityjson.run()
tok = process_time()
print(f"GeoJSON to CityJSON took {tok-tik} seconds.")