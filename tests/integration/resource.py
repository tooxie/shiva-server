# -*- coding: utf-8 -*-
import os
import tempfile
import unittest
import random

from flask import json

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
        shiva.app.config['ALLOW_ANONYMOUS_ACCESS'] = False
        shiva.app.config['CONVERTER_CLASS'] = ConverterMock
        shiva.app.config['UPLOAD_HANDLER'] = UploadHandlerMock

        self.ctx = shiva.app.test_request_context()
        self.ctx.push()

        shiva.db.create_all()

        self.artist = Artist(name='4no1')
        self.album = Album(name='Falling down')
        self.track = Track(title='Falling down', path='/music/4no1/01.mp3',
                           hash_file=False, no_metadata=True)
        self.album.artists.append(self.artist)
        self.user = User(email='derp@mail.com', password='blink182',
                         is_public=True, is_active=True, is_admin=False)

        shiva.db.session.add(self.artist)
        shiva.db.session.add(self.album)
        shiva.db.session.add(self.track)
        shiva.db.session.add(self.user)
        shiva.db.session.commit()

        self._app = shiva.app
        self._db = shiva.db
        self.app = shiva.app.test_client()

        self.artist_pk = self.artist.pk
        self.album_pk = self.album.pk
        self.track_pk = self.track.pk
        self.user_pk = self.user.pk

    def mk_track(self):
        name = str(random.random())
        track = Track(title=name, path='/music/band/%s.mp3' % name,
                      hash_file=False, no_metadata=True)

        self._db.session.add(track)
        self._db.session.commit()

        return track

    def mk_user(self, is_public=True, is_active=True, is_admin=False):
        email = str(random.random())
        password = str(random.random())

        user = User(email=email, password=password, is_public=is_public,
                    is_active=is_active, is_admin=is_admin)

        self._db.session.add(user)
        self._db.session.commit()

        return user

    def tearDown(self):
        self.ctx.pop()
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def authenticate(self):
        """Logs a user in and returns the corresponding authentication token.
        """

        if hasattr(self, 'auth_token'):
            return self.auth_token

        url = '/users/login/'
        payload = dict(email='derp@mail.com', password='blink182')
        rv = json.loads(self.app.post(url, data=payload).data)
        self.auth_token = rv['token']

        return self.auth_token

    def do_request(self, method, *args, **kwargs):
        """
        Wrapper around flask's test client. It understands shiva's token-based
        authentication and performs a login before the request, unless
        otherwise specified.
        """

        _args = list(args)

        authenticate = kwargs.get('authenticate', True)
        if authenticate:
            token = self.authenticate()
            _args[0] = '%s%stoken=%s' % (args[0],
                                         '&' if '?' in args[0] else '?',
                                         token)

        if 'authenticate' in kwargs:
            del(kwargs['authenticate'])

        func = getattr(self.app, method)
        rv = func(*_args, **kwargs)
        try:
            rv.json = json.loads(rv.data)
            rv.is_json = True
        except:
            rv.json = None
            rv.is_json = False

        return rv

    def get(self, *args, **kwargs):
        return self.do_request('get', *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.do_request('post', *args, **kwargs)

    def put(self, *args, **kwargs):
        return self.do_request('put', *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.do_request('delete', *args, **kwargs)
