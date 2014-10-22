# Copyright 2014 (C) Rich Wareham <rich.cusf@richwareham.com>
#
# This file is part of Ruaumoko.
# https://github.com/cuspaceflight/ruaumoko
#
# Ruaumoko is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ruaumoko is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ruaumoko. If not, see <http://www.gnu.org/licenses/>.
"""
Tests for the ruaumoko download code.

"""
import logging
import os
from unittest import TestCase

# NB: unittest.mock is part of the standard lib in later Pythons
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import responses

import ruaumoko.download as rd

from .util import TemporaryDirectoryTestCase, responses_add_dem_mocks

LOG = logging.getLogger(__name__)

class TestFullStackDownloader(TemporaryDirectoryTestCase):
    def __init__(self, *args, **kwargs):
        super(TestFullStackDownloader, self).__init__(*args, **kwargs)

    def create_workspace_dir(self):
        """Create a temporary workspace directory for the downloader to work in."""
        ws_dir = os.path.join(self.tmp_dir, 'workspace')
        LOG.info('Making downloader temporary workspace directory at {0}'.format(ws_dir))
        os.mkdir(ws_dir)
        return ws_dir

    def prepare_single_file_download(self):
        """Create workspace and pathnames for a single-dataset download.

        """
        # Make downloader's temporary directory
        ws_dir = self.create_workspace_dir()

        # Where to download to
        tgt_path = os.path.join(self.tmp_dir, 'dataset')
        LOG.info('Downloading to {0}'.format(tgt_path))

        return ws_dir, tgt_path

    def check_single_file_download(self, n_chunks, tgt_path, ws_dir):
        """Check a single-file download."""

        # We expect the size of the file to correspond to the right number of chunks
        expected_size = n_chunks * (8 * 8 * 2)
        tgt_size = os.stat(tgt_path).st_size
        LOG.info('Downloaded data size is {0}, expecting {1}'.format(tgt_size, expected_size))
        self.assertEqual(tgt_size, expected_size)

        # We expect the temporary workspace to be empty
        ws_list = os.listdir(ws_dir)
        LOG.info('Workspace directory contents: {0}'.format(ws_list))
        self.assertEqual(len(ws_list), 0)

    @responses.activate
    def test_download_two_chunks(self):
        responses_add_dem_mocks()
        ws_dir, tgt_path = self.prepare_single_file_download()

        with open(tgt_path, 'wb') as tgt:
            rd.download(tgt, ws_dir, chunks=('A', 'X'), expect_res=(8,8))

        self.check_single_file_download(2, tgt_path, ws_dir)

    @responses.activate
    def test_download_all_chunks(self):
        responses_add_dem_mocks()
        ws_dir, tgt_path = self.prepare_single_file_download()

        with open(tgt_path, 'wb') as tgt:
            rd.download(tgt, ws_dir, expect_res=(8,8))

        self.check_single_file_download(24, tgt_path, ws_dir)

    def prepare_multiple_chunk_download(self):
        """Create workspace and pathnames for a multi-chunk download.

        """
        # Make downloader's temporary directory
        ws_dir = self.create_workspace_dir()

        # Make directory to store chunks
        chunk_dir = os.path.join(self.tmp_dir, 'chunks')
        LOG.info('Making chunk directory at {0}'.format(chunk_dir))
        os.mkdir(chunk_dir)

        return ws_dir, chunk_dir

    def check_multiple_chunk_download(self, n_chunks, ws_dir, chunk_dir,
            expect_prefix, expect_suffix):
        """Check a multi-chunk download."""

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

    def download_all_chunks_separately(self, prefix=None, expect_prefix='15-',
            expect_suffix='.tif'):
        ws_dir, chunk_dir = self.prepare_multiple_chunk_download()

        # Kick off download
        rd.download(None, ws_dir, expect_res=(8,8),
                chunk_directory=chunk_dir, chunk_prefix=prefix)

        self.check_multiple_chunk_download(24, ws_dir, chunk_dir, expect_prefix, expect_suffix)

    @responses.activate
    def test_download_all_chunks_separately(self):
        responses_add_dem_mocks()
        self.download_all_chunks_separately()

    @responses.activate
    def test_download_all_chunks_separately_with_prefix(self):
        responses_add_dem_mocks()

        # Note that auto-named chunks have the extension '.tiff'
        self.download_all_chunks_separately(prefix='chunk-',
                expect_prefix='chunk-', expect_suffix='.tiff')

    @responses.activate
    def test_download_all_chunks_via_main(self):
        responses_add_dem_mocks()

        ws_dir, tgt_path = self.prepare_single_file_download()
        new_argv = ['ruaumoko-download', '--expect-resolution', '8x8', tgt_path]
        with patch('sys.argv', new_argv):
            status = rd.main()

        self.assertEqual(status, 0)
        self.check_single_file_download(24, tgt_path, ws_dir)

    @responses.activate
    def test_download_split_chunks_via_main(self):
        responses_add_dem_mocks()

        ws_dir, chunk_dir = self.prepare_multiple_chunk_download()
        new_argv = ['ruaumoko-download', '--expect-resolution', '8x8',
                '--split-chunks', chunk_dir]
        with patch('sys.argv', new_argv):
            status = rd.main()

        self.assertEqual(status, 0)
        self.check_multiple_chunk_download(24, ws_dir, chunk_dir, '15-', '.tif')

    @responses.activate
    def test_bad_resolution_spec_non_numeric(self):
        responses_add_dem_mocks()
        ws_dir, tgt_path = self.prepare_single_file_download()
        new_argv = ['ruaumoko-download', '--expect-resolution', 'WxZ', tgt_path]
        with patch('sys.argv', new_argv):
            status = rd.main()
        self.assertEqual(status, 1)

    @responses.activate
    def test_bad_resolution_spec_too_many_items(self):
        responses_add_dem_mocks()
        ws_dir, tgt_path = self.prepare_single_file_download()
        new_argv = ['ruaumoko-download', '--expect-resolution', '8x8x1', tgt_path]
        with patch('sys.argv', new_argv):
            status = rd.main()
        self.assertEqual(status, 1)
