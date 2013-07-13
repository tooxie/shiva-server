# -*- coding: utf-8 -*-
from nose import tools as nose
import unittest

from shiva.app import app, db
from shiva.indexer import Indexer


class IndexerTestCase(unittest.TestCase):

    def setUp(self):
        db.create_all()

    def test_main(self):
        with app.app_context():
            app.config['MEDIA_DIRS'] = []
            lola = Indexer(app.config)
            nose.eq_(lola.run(), None)

    def tearDown(self):
        db.drop_all()
