# -*- coding: utf-8 -*-
from mock import Mock
try:
    import unittest2 as unittest
except ImportError:
    import unittest
import os

from shiva.indexer.main import Indexer


class IndexerTestCase(unittest.TestCase):

    def setUp(self):
        self.config = {
            'MEDIA_DIRS': [],
            'VALID_FILE_EXTENSIONS': ('mp3',),
        }
        self.indexer = Indexer(self.config)

        os.path.isfile = Mock()

    def test_track_detection(self):
        self.indexer.file_path = 'valid_track.mp3'

        self.assertTrue(self.indexer.is_track())

    def test_extension_detection(self):
        self.indexer.file_path = 'valid_track.mp3'

        self.assertEqual(self.indexer.get_extension(), 'mp3')

    def test_runs(self):
        self.assertIsNone(self.indexer.run())
