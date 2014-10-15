# -*- coding: utf-8 -*-
from datetime import datetime

from nose import tools as nose

from .resource import ResourceTestCase


class StatusCodesTestCase(ResourceTestCase):
    # Unauthorized
    def test_unauthorized_root(self):
        resp = self.get('/', authenticate=False)
        nose.eq_(resp.status_code, 401)

        resp = self.get('/whatsnew/', authenticate=False)
        nose.eq_(resp.status_code, 401)

        resp = self.get('/clients/', authenticate=False)
        nose.eq_(resp.status_code, 401)

        resp = self.get('/about/', authenticate=False)
        nose.eq_(resp.status_code, 401)

    # Authorized
    def test_root(self):
        resp = self.get('/')
        nose.eq_(resp.status_code, 404)

    def test_whatsnew(self):
        resp = self.get('/whatsnew/?since=20101010')
        nose.eq_(resp.status_code, 200)

    def test_clients(self):
        resp = self.get('/clients/')
        nose.eq_(resp.status_code, 200)

    def test_about(self):
        resp = self.get('/about/')
        nose.eq_(resp.status_code, 200)
