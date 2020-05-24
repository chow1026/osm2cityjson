
from enum import Enum


class GeoJSONObjectTypes(Enum):
    Feature = {
        "type": "Feature",
        "geometry": None,       # Dict with shape `type` & `coordinates`
        "properties": None}     # Dict of attributes
    FeatureCollection = {
        "type": "FeatureCollection",
        "features": None}       # List of feature object


class GeoJSON:
    def __init__(self, geojson_type: GeoJSONObjectTypes, name: str = None):
        self.geojson_type = geojson_type
        self.geojson = geojson_type.value
        if name:
            self.name = name
            self.geojson["name"] = name

    def get_geojson(self):
        return self.geojson