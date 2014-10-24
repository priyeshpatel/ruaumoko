import logging
from tempfile import mkdtemp
import os
from shutil import rmtree
from unittest import TestCase
import zipfile

import responses

from ruaumoko._compat import urlunsplit

LOG = logging.getLogger(__name__)
DATA_DIR = os.path.join(os.path.dirname(__file__), 'mock-data')

# Path to the mock ruaumoko dataset and the tile-size within
MOCK_DATASET_PATH = os.path.join(DATA_DIR, 'dem-dataset')
MOCK_DATASET_TILE_SIZE = (20,10)

class TemporaryDirectoryTestCase(TestCase):
    def setUp(self):
        super(TemporaryDirectoryTestCase, self).setUp()

        # Create a temporary directory which we can scribble over
        self.tmp_dir = mkdtemp(prefix='ruaumoko.test.')
        LOG.info('Created temporary directory {0}'.format(self.tmp_dir))

    def tearDown(self):
        # Remove the directory which we created
        LOG.info('Removing temporary directory {0}'.format(self.tmp_dir))
        rmtree(self.tmp_dir)
        self.tmp_dir = None

        super(TemporaryDirectoryTestCase, self).tearDown()

def responses_add_dem_mocks(host='www.viewfinderpanoramas.org', path='DEM/TIF15'):
    """Register mock HTTP responses for mock DEM data.

    """
    mock_zip = zipfile.ZipFile(os.path.join(DATA_DIR, 'dem-chunks.zip'))
    url_root = urlunsplit(('http', host, path, '', ''))
    for info in mock_zip.infolist():
        file_url = url_root + '/' + info.filename
        LOG.info('Adding mock response for ' + file_url)
        responses.add(responses.GET, file_url,
                body=mock_zip.open(info).read(),
                content_type='application/zip')

