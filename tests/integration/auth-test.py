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

        self.ctx = shiva.app.test_request_context()
        self.ctx.push()

        shiva.db.create_all()

        self.user = User(email='derp@mail.com', password='blink182',
                         is_public=False, is_active=True)
        shiva.db.session.add(self.user)
        shiva.db.session.commit()

        self.app = shiva.app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)
        self.ctx.pop()

    def get_payload(self):
        return {
            'email': 'derp@mail.com',
            'password': 'blink182',
        }

    def test_valid_login(self):
        rv = self.app.post('/users/login/', data=self.get_payload())
        nose.eq_(rv.status_code, 200)
        resp = json.loads(rv.data)
        nose.ok_(resp.has_key('token'))

    def test_invalid_login(self):
        payload = {
            'email': 'fake',
            'password': 'f4k3',
        }
        rv = self.app.post('/users/login/', data=payload)
        nose.eq_(rv.status_code, 401)

    def test_invalid_password(self):
        payload = self.get_payload().update({
            'password': 'f4k3',
        })
        rv = self.app.post('/users/login/', data=payload)
        nose.eq_(rv.status_code, 401)
