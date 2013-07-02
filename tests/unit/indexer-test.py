# -*- coding: utf-8 -*-
from nose import tools as nose
import unittest

from shiva.app import app
from shiva.indexer import Indexer


class IndexerTestCase(unittest.TestCase):

    def test_main(self):
        with app.app_context():
            lola = Indexer(app.config)
            nose.eq_(lola.run(), None)
