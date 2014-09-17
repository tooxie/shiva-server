# -*- coding: utf-8 -*-
import os
import tempfile
import unittest

from shiva import app as shiva
from shiva.converter import Converter
from shiva.models import Artist, Album, Track, User
from shiva.resources.upload import UploadHandler


class ConverterMock(Converter):
    def get_uri(self):
        return 'http://127.0.0.1:8000%s' % self.track


class UploadHandlerMock(UploadHandler):
    path = '/some/path.mp3'

    def __init__(self, *args, **kwargs):
        pass

    def save(self):
        pass

    def __getattr__(self, *args, **kwargs):
        return None


class ResourceTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        db_uri = 'sqlite:///%s' % self.db_path
        shiva.app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
        shiva.app.config['TESTING'] = True
        shiva.app.config['ALLOW_DELETE'] = True
        shiva.app.config['CONVERTER_CLASS'] = ConverterMock
        shiva.app.config['UPLOAD_HANDLER'] = UploadHandlerMock

        with shiva.app.test_request_context():
            shiva.db.create_all()

            self.artist = Artist(name='4no1')
            self.album = Album(name='Falling down')
            self.track = Track(title='Falling down', path='/music/4no1/01.mp3',
                               hash_file=False, no_metadata=True)
            self.album.artists.append(self.artist)
            self.user = User(email='derp@mail.com', password='blink182')

            shiva.db.session.add(self.artist)
            shiva.db.session.add(self.album)
            shiva.db.session.add(self.track)
            shiva.db.session.add(self.user)
            shiva.db.session.commit()

            self.app = shiva.app.test_client()

            self.artist_pk = self.artist.pk
            self.album_pk = self.album.pk
            self.track_pk = self.track.pk
            self.user_pk = self.user.pk

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)
