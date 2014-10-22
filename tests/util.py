import logging
from tempfile import mkdtemp
from unittest import TestCase
from shutil import rmtree

LOG = logging.getLogger(__name__)

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


