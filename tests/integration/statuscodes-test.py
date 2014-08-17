# -*- coding: utf-8 -*-
from nose import tools as nose
import os
import tempfile
import unittest

from shiva import app as shiva


class StatusCodesTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        db_uri = 'sqlite:///%s' % self.db_path
        shiva.app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
        shiva.app.config['TESTING'] = True
        shiva.app.config['ALLOW_DELETE'] = False
        shiva.db.create_all()
        self.app = shiva.app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_root(self):
        rv = self.app.get('/')
        nose.eq_(rv.status_code, 404)

    def test_artists(self):
        rv = self.app.get('/artists')
        nose.eq_(rv.status_code, 200)

    def test_artist_404(self):
        rv = self.app.get('/artists/1')
        nose.eq_(rv.status_code, 404)

    def test_albums(self):
        rv = self.app.get('/albums')
        nose.eq_(rv.status_code, 200)

    def test_album_404(self):
        rv = self.app.get('/albums/1')
        nose.eq_(rv.status_code, 404)

    def test_tracks(self):
        rv = self.app.get('/tracks')
        nose.eq_(rv.status_code, 200)

    def test_track_404(self):
        rv = self.app.get('/tracks/1')
        nose.eq_(rv.status_code, 404)

    def test_delete_not_allowed(self):
        rv = self.app.delete('/tracks/1')
        nose.eq_(rv.status_code, 405)
