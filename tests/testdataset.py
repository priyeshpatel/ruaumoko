from tempfile import mkdtemp
from shutil import rmtree
import logging
import os

from .util import DownloadedDatasetTestCase

from ruaumoko import Dataset

LOG = logging.getLogger(__name__)

class TestGet(DownloadedDatasetTestCase):
    def test_dataset_was_downloaded(self):
        """Checks that a dataset was downloaded."""
        assert os.path.isfile(self.dataset_path)
        assert os.stat(self.dataset_path).st_size > 0

    def test_create_dataset(self):
        """Check a dataset may be successfully opened."""
        ds = Dataset(self.dataset_path, expected_res=(20,10))
