# -*- coding: utf-8 -*-
import os
import tempfile
import unittest

from shiva import app as shiva
from shiva.models import Artist, Album


class ResourceTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        db_uri = 'sqlite:///%s' % self.db_path
        shiva.app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
        shiva.app.config['TESTING'] = True
        shiva.app.config['ALLOW_DELETE'] = True
        shiva.db.create_all()

        self.app = shiva.app.test_client()

        self.artist = Artist(name='4no1')
        self.album = Album(name='Falling down')
        self.album.artists.append(self.artist)

        shiva.db.session.add(self.artist)
        shiva.db.session.add(self.album)
        shiva.db.session.commit()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)
