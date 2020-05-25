### README

This is simple command line tool to parse osm (XML) and generate CityJSON format. 

#### Installation:
1. Git clone the [osm2cityjson]() repository from GitHub.
2. At the root of the directory, `python3 setup.py install`.

#### Usage:
osm2cityjson [OPTIONS]


Options:

- `-i` | `--input_file` 
    - PATH
    - Specify input file.  
    - [required]
- `-o` | `--output_dir`
    - PATH
    - Specify output file directory. Input file basename will be used, but amended with appropriate output file extension. 
    - [required]
- `-d` | `--debug_mode` 
    - BOOLEAN 
    - Enable/Disable debug mode
    - [default: False; required]
- `-gjson` | `--output_geojson`
    - BOOLEAN
    - Whether or not to output alternate geojson format.  
    - [default: False]
- `--help`
    - Show help message and exit.
