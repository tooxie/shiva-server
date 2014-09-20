# -*- coding: utf-8 -*-
from nose import tools as nose

from flask import json

from tests.integration.resource import ResourceTestCase


class UsersResourceTestCase(ResourceTestCase):

    def get_payload(self):
        return {
            'email': 'derpina@herp.com',
            'password': 'blink182',
        }

    def test_user_base_resource(self):
        rv = self.app.get('/users')
        nose.eq_(rv.status_code, 405)

    def test_nonexistent_user(self):
        rv = self.app.get('/users/123')
        nose.eq_(rv.status_code, 404)

    def test_user_creation(self):
        rv = self.app.post('/users', data=self.get_payload())
        resp = json.loads(rv.data)

        nose.eq_(rv.status_code, 201)

        _rv = self.app.post('/users', data=self.get_payload())
        nose.eq_(_rv.status_code, 409)  # Conflict

    def test_user_deletion(self):
        # The correct status code in this case would be 405, but to prevent
        # brute-force attacks we return always 404.
        rv = self.app.delete('/users/%i' % self.user.pk)
        nose.eq_(rv.status_code, 404)
