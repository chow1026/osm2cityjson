from pathlib import Path

from setuptools import setup, find_packages

import osm2cityjson


CURRENT_DIR = Path(__file__).parent

with open("README.md", "r") as fh:
    long_description = fh.read()

required_packages = [
    'geopandas',
    'Shapely',
    'Fiona',
    'scipy',
    'jsonref',
    'click',
    'jsonschema'
]

setup(
    name='osm2cityjson',
    version=osm2cityjson.__version__,
    description='Converter of OSM (XML) to CityJSON. Currently only support '
                'Building Objects',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/chow1026/osm2cityjson',
    python_requires='~=3.7',
    packages=find_packages(),
    install_requires=required_packages,
    entry_points={
          'console_scripts': ['osm2cityjson=osm2cityjson.core:cli']
    },
)
