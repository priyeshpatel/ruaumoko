import logging
import os
from tempfile import mkdtemp
from unittest import TestCase
from shutil import rmtree
import zipfile

import responses

import ruaumoko.download as rd
from ruaumoko._compat import urlunsplit

LOG = logging.getLogger(__name__)
DATA_DIR = os.path.join(os.path.dirname(__file__), 'mock-data')

class TemporaryDirectoryTestCase(TestCase):
    def setUp(self):
        super(TemporaryDirectoryTestCase, self).setUp()

        # Create a temporary directory which we can scribble over
        self.tmp_dir = mkdtemp()
        LOG.info('Created temporary directory {0}'.format(self.tmp_dir))

    def tearDown(self):
        # Remove the directory which we created
        LOG.info('Removing temporary directory {0}'.format(self.tmp_dir))
        rmtree(self.tmp_dir)
        self.tmp_dir = None

        super(TemporaryDirectoryTestCase, self).tearDown()

class TestFullStackDownloader(TemporaryDirectoryTestCase):
    def __init__(self, *args, **kwargs):
        super(TestFullStackDownloader, self).__init__(*args, **kwargs)

        # Load mock data
        self.mock_zip = zipfile.ZipFile(os.path.join(DATA_DIR, 'dem-chunks.zip'))

    def responses_add_mocks(self, host='www.viewfinderpanoramas.org', path='DEM/TIF15'):
        url_root = urlunsplit(('http', host, path, '', ''))
        for info in self.mock_zip.infolist():
            file_url = url_root + '/' + info.filename
            LOG.info('Adding mock response for ' + file_url)
            responses.add(responses.GET, file_url,
                    body=self.mock_zip.open(info).read(),
                    content_type='application/zip')

    @responses.activate
    def test_download_two_chunks(self):
        # Add mock data to responses
        self.responses_add_mocks()

        # Make downloader's temporary directory
        ws_dir = os.path.join(self.tmp_dir, 'workspace')
        LOG.info('Making downloader temporary workspace directory at {0}'.format(ws_dir))
        os.mkdir(ws_dir)

        # Where to download to
        tgt_path = os.path.join(self.tmp_dir, 'dataset')
        LOG.info('Downloading to {0}'.format(tgt_path))

        # Kick off download
        with open(tgt_path, 'wb') as tgt:
            rd.download(tgt, ws_dir, chunks=('A', 'X'), expect_size=8*8*2)

        # We expect the size of the file to correspond to two chunks
        expected_size = 2 * (8 * 8 * 2)
        tgt_size = os.stat(tgt_path).st_size
        LOG.info('Downloaded data size is {0}, expecting {1}'.format(tgt_size, expected_size))
        self.assertEqual(tgt_size, expected_size)

        # We expect the temporary workspace to be empty
        ws_list = os.listdir(ws_dir)
        LOG.info('Workspace directory contents: {0}'.format(ws_list))
        self.assertEqual(len(ws_list), 0)

    @responses.activate
    def test_download_all_chunks(self):
        # Add mock data to responses
        self.responses_add_mocks()

        # Make downloader's temporary directory
        ws_dir = os.path.join(self.tmp_dir, 'workspace')
        LOG.info('Making downloader temporary workspace directory at {0}'.format(ws_dir))
        os.mkdir(ws_dir)

        # Where to download to
        tgt_path = os.path.join(self.tmp_dir, 'dataset')
        LOG.info('Downloading to {0}'.format(tgt_path))

        # Kick off download
        with open(tgt_path, 'wb') as tgt:
            rd.download(tgt, ws_dir, expect_size=8*8*2)

        # We expect the size of the file to correspond to 24 chunks
        expected_size = 24 * (8 * 8 * 2)
        tgt_size = os.stat(tgt_path).st_size
        LOG.info('Downloaded data size is {0}, expecting {1}'.format(tgt_size, expected_size))
        self.assertEqual(tgt_size, expected_size)

        # We expect the temporary workspace to be empty
        ws_list = os.listdir(ws_dir)
        LOG.info('Workspace directory contents: {0}'.format(ws_list))
        self.assertEqual(len(ws_list), 0)

    def download_all_chunks_separately(self, prefix=None,
            expect_prefix='15-', expect_suffix='.tif'):
        # Make downloader's temporary directory
        ws_dir = os.path.join(self.tmp_dir, 'workspace')
        LOG.info('Making downloader temporary workspace directory at {0}'.format(ws_dir))
        os.mkdir(ws_dir)

        # Where to download to
        tgt_path = os.path.join(self.tmp_dir, 'dataset')
        LOG.info('Downloading to {0}'.format(tgt_path))

        # Make directory to download chunks to
        chunk_dir = os.path.join(self.tmp_dir, 'chunks')
        LOG.info('Making downloader temporary chunk directory at {0}'.format(chunk_dir))
        os.mkdir(chunk_dir)

        # Kick off download
        rd.download(None, ws_dir, expect_size=8*8*2, chunk_directory=chunk_dir, chunk_prefix=prefix)

        # We expect the temporary workspace to be empty
        ws_list = os.listdir(ws_dir)
        LOG.info('Workspace directory contents: {0}'.format(ws_list))
        self.assertEqual(len(ws_list), 0)

        # We expect to find a load of TIFF files in the chunk_dir
        chunk_files = os.listdir(chunk_dir)
        LOG.info('Chunk directory has {0} files'.format(len(chunk_files)))
        self.assertEqual(len(chunk_files), 24)

        # Each chunk file should be a .tif
        for fn in chunk_files:
            LOG.info('Chunk was downloaded to: {0}'.format(fn))
            self.assertTrue(fn.endswith(expect_suffix))
            self.assertTrue(fn.startswith(expect_prefix))

    @responses.activate
    def test_download_all_chunks_separately(self):
        self.responses_add_mocks()
        self.download_all_chunks_separately()

    @responses.activate
    def test_download_all_chunks_separately_with_prefix(self):
        self.responses_add_mocks()
        # Note that auto-named chunks have the extension '.tiff'
        self.download_all_chunks_separately(prefix='chunk-',
                expect_prefix='chunk-', expect_suffix='.tiff')
