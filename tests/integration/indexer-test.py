# -*- coding: utf-8 -*-
from nose import tools as nose
import os
import tempfile
import unittest

from shiva import app as shiva
from shiva.indexer import Indexer


class IndexerTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        db_uri = 'sqlite:///%s' % self.db_path
        shiva.app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
        shiva.app.config['TESTING'] = True
        shiva.db.create_all()

        self.app = shiva.app.test_client()

    def test_main(self):
        with shiva.app.test_request_context():
            shiva.app.config['MEDIA_DIRS'] = []
            lola = Indexer(shiva.app.config)
            nose.eq_(lola.run(), None)

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)
