import time
import xml.sax
from pathlib import Path
from typing import Tuple

from util.util import is_valid_filepath
from osm.osm_content_handler import OSMContentHandler
from util.logging import Logger


class OSM:
    def __init__(self, input_filepath: Path, handler: OSMContentHandler,
                 logger: Logger, output_dir: Path = None):
        self.input_filepath = input_filepath
        self.output_dir = output_dir
        self.logger = logger
        self.handler = handler
        self.ways = {}
        self.nodes = {}
        if not is_valid_filepath(input_filepath):
            self.logger.log_error(f"Invalid input file.")

    def run(self) -> Tuple[dict, dict]:
        tic = time.process_time()
        self._parse_xml_content()
        toc = time.process_time()
        print(f"Parsing OSM took {toc-tic} seconds.")
        return self.ways, self.nodes

    def _parse_xml_content(self):
        with open(str(self.input_filepath), mode='rb') as osm:
            xml.sax.parse(osm, self.handler)
            self.ways = self.handler.object["elements"]["ways"]
            self.nodes = self.handler.object["elements"]["nodes"]
        print(len(self.ways), len(self.nodes))
