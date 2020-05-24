import json
import os
import shutil
from pathlib import Path

from tests import BaseTest
from util.util import is_valid_filepath, is_valid_dirpath


class BaseTestUtil(BaseTest):
    def setUp(self):
        self._make_test_dir(self.test_output_dir)
        self.valid_filepath = self.fixture_dir / "sample-buildings.osm"
        self.invalid_filepath = self.fixture_dir / "non-existing.osm"
        self.valid_dirpath = self.test_output_dir
        self.invalid_dirpath = Path("non_existing_dir/")

    def test_is_valid_filepath(self):
        self.assertEqual(is_valid_filepath(self.valid_filepath), True)
        self.assertEqual(is_valid_filepath(self.invalid_filepath), False)

    def test_is_valid_dirpath(self):
        self.assertEqual(is_valid_dirpath(self.valid_dirpath), True)
        self.assertEqual(is_valid_dirpath(self.invalid_dirpath), False)