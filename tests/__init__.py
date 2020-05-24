import os
import shutil
from pathlib import Path
from unittest import TestCase

from util.logging import Logger


class BaseTest(TestCase):
    logger = Logger(debug=True)

    @classmethod
    def setUpClass(cls):
        cls.fixture_dir = Path("tests/fixtures").absolute()
        cls.test_output_dir = Path("tests/output").absolute()

    def setUp(self):
        self._make_test_dir(self.test_output_dir)

    def tearDown(self):
        pass
        # shutil.rmtree(self.test_output_dir)

    @staticmethod
    def _make_test_dir(test_dir: str):
        os.makedirs(test_dir, exist_ok=True)
