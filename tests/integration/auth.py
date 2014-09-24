# -*- coding: utf-8 -*-
import os
import tempfile
import unittest

from nose import tools as nose
from flask import json

from shiva import app as shiva
from shiva.models import Artist, Album, User


class AuthTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        db_uri = 'sqlite:///%s' % self.db_path
        shiva.app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
        shiva.app.config['TESTING'] = True
        shiva.app.config['ALLOW_ANONYMOUS_ACCESS'] = False
        with shiva.app.test_request_context():
            shiva.db.create_all()

            self.user = User(email='derp@mail.com', password='blink182',
                             is_active=True, is_admin=False)
            shiva.db.session.add(self.user)

            shiva.db.session.commit()

            self.app = shiva.app.test_client()
            self.auth_token = self.get_token()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def get_payload(self):
        return {
            'email': 'derp@mail.com',
            'password': 'blink182',
        }

    def get_token(self):
        rv = self.app.post('/users/login', data=self.get_payload())
        resp = json.loads(rv.data)

        return resp['token']

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

    def test_unauthorized_creation_of_artist(self):
        rv = self.app.post('/artists', data={})
        nose.eq_(rv.status_code, 401)

    def test_valid_login(self):
        rv = self.app.post('/users/login', data=self.get_payload())
        nose.eq_(rv.status_code, 200)
        resp = json.loads(rv.data)
        nose.ok_(resp.has_key('token'))

    def test_invalid_login(self):
        payload = {
            'email': 'fake',
            'password': 'f4k3',
        }
        rv = self.app.post('/users/login', data=payload)
        nose.eq_(rv.status_code, 401)

    def test_invalid_password(self):
        payload = self.get_payload().update({
            'password': 'f4k3',
        })
        rv = self.app.post('/users/login', data=payload)
        nose.eq_(rv.status_code, 401)

    def test_authorized_access_to_albums(self):
        rv = self.app.get('/albums?token=%s' % self.auth_token)
        nose.eq_(rv.status_code, 200)

    def test_authorized_access_to_artists(self):
        rv = self.app.get('/artists?token=%s' % self.auth_token)
        nose.eq_(rv.status_code, 200)

    def test_authorized_access_to_tracks(self):
        rv = self.app.get('/tracks?token=%s' % self.auth_token)
        nose.eq_(rv.status_code, 200)

    def test_authorized_creation_of_artist(self):
        url = '/artists?token=%s' % self.auth_token
        rv = self.app.post(url, data={'name': 'Troy McClure'})
        nose.eq_(rv.status_code, 201)
        resp = json.loads(rv.data)

        url = '/artists/%s?token=%s' % (resp['id'], self.auth_token)
        rv = self.app.get(url)
        nose.eq_(rv.status_code, 200)
