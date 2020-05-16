from osm2cityjson.core import OSM2GeoJSON
from pathlib import Path
from time import process_time


intermediat_dir = Path("data")
input_file = Path("data/singapore-buildings.osm")

tik = process_time()
OSM2GeoJSON(input_filepath=input_file, intermediate_dir=intermediat_dir).run()
tok = process_time()
print(f"Whole process took {tok-tik} seconds.")