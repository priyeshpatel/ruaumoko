from tempfile import mkdtemp
from shutil import rmtree
import logging
import os
from unittest import TestCase

from .util import MOCK_DATASET_PATH

from ruaumoko import Dataset

LOG = logging.getLogger(__name__)

class TestGet(TestCase):
    def test_dataset_was_downloaded(self):
        """Checks that a dataset was downloaded."""
        assert os.path.isfile(MOCK_DATASET_PATH)
        assert os.stat(MOCK_DATASET_PATH).st_size > 0

    def test_create_dataset(self):
        """Check a dataset may be successfully opened."""
        ds = Dataset(MOCK_DATASET_PATH, expected_res=(20,10))
