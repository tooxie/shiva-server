# -*- coding: utf-8 -*-
import os
import tempfile
import unittest

from shiva import app as shiva
from shiva.models import Artist, Album, User


class AuthTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        db_uri = 'sqlite:///%s' % self.db_path
        shiva.app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
        shiva.app.config['TESTING'] = True
        shiva.app.config['ALLOW_ANONYMOUS_ACCESS'] = False
        shiva.db.create_all()

        self.app = shiva.app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_unauthorized_access_to_albums(self):
        rv = self.app.get('/albums')
        nose.eq_(rv.status_code, 401)

    def test_unauthorized_creation_of_albums(self):
        rv = self.app.post('/albums', data={})
        nose.eq_(rv.status_code, 401)

    def test_unauthorized_access_to_artists(self):
        rv = self.app.get('/artists')
        nose.eq_(rv.status_code, 401)

    def test_unauthorized_creation_of_artists(self):
        rv = self.app.post('/artists', data={})
        nose.eq_(rv.status_code, 401)

    def test_unauthorized_access_to_tracks(self):
        rv = self.app.get('/artists')
        nose.eq_(rv.status_code, 401)

    def test_unauthorized_creation_of_tracks(self):
        rv = self.app.post('/tracks', data={})
        nose.eq_(rv.status_code, 401)
