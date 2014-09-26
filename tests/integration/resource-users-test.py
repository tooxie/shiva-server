# -*- coding: utf-8 -*-
from flask import json
from nose import tools as nose

from tests.integration.resource import ResourceTestCase


class UsersResourceTestCase(ResourceTestCase):
    """
    GET /users
        401 Unauthorized
        405 Method Not Allowed
    POST /users email=<str> [display_name=<str>] [password=<str>]
                [is_active=<bool>] [is_admin=<bool>]
        201 Created
        400 Bad Request
        401 Unauthorized
        409 Conflict
    GET /users/me
        200 OK
        401 Unauthorized
    POST /users/me
        401 Unauthorized
        405 Method Not Allowed
    PUT /users/me
        401 Unauthorized
        405 Method Not Allowed
    DELETE /users/me
        401 Unauthorized
        405 Method Not Allowed
    GET /users/<id>
        200 OK
        401 Unauthorized
        404 Not Found
    PUT /users/<id> [email=<str>] [display_name=<str>] [password=<str>]
                    [is_active=<bool>] [is_admin=<bool>]
        204 No Content
        400 Bad Request (If email is unset)
        401 Unauthorized
        404 Not Found
        409 Conflict
    DELETE /users/<id>
        204 No Content
        401 Unauthorized
        404 Not Found
    """

    def get_payload(self):
        return {
            'email': 'derpina@herp.com',
            'password': 'blink182',
            'is_active': True,
            'is_admin': False,
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
