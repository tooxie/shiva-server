# -*- coding: utf-8 -*-
from nose import tools as nose

from shiva.auth import Roles
from tests.integration.resource import ResourceTestCase


class UsersResourceTestCase(ResourceTestCase):
    """
    GET /users/
        401 Unauthorized
        405 Method Not Allowed
    POST /users/ email=<str> [display_name=<str>] [password=<str>]
                [is_active=<bool>] [is_admin=<bool>]
        201 Created
        400 Bad Request
        401 Unauthorized
        409 Conflict
    GET /users/me/
        200 OK
        401 Unauthorized
    POST /users/me/
        401 Unauthorized
        405 Method Not Allowed
    PUT /users/me/
        401 Unauthorized
        405 Method Not Allowed
    DELETE /users/me/
        401 Unauthorized
        405 Method Not Allowed
    GET /users/<id>/
        200 OK
        401 Unauthorized
        404 Not Found
    PUT /users/<id>/ [email=<str>] [display_name=<str>] [password=<str>]
                    [is_active=<bool>] [is_admin=<bool>]
        204 No Content
        400 Bad Request (If email is unset)
        401 Unauthorized
        404 Not Found
        409 Conflict
    DELETE /users/<id>/
        204 No Content
        401 Unauthorized
        404 Not Found
    """

    def get_payload(self):
        return {
            'email': 'derpina@herp.com',
            'display_name': 'derpina',
            'password': 'blink182',
            'is_active': True,
            'role': Roles.USER,
        }

    # Unauthorized
    def test_unauthorized_user_base_resource(self):
        resp = self.get('/users/', authenticate=False)
        nose.eq_(resp.status_code, 401)

        resp = self.get('/users/me/', authenticate=False)
        nose.eq_(resp.status_code, 401)

        resp = self.get('/users/1/', authenticate=False)
        nose.eq_(resp.status_code, 401)

        # POST
        payload = self.get_payload()
        resp = self.post('/users/', data=payload, authenticate=False)
        nose.eq_(resp.status_code, 401)

        # PUT
        payload = self.get_payload()
        resp = self.put('/users/', data=payload, authenticate=False)
        nose.eq_(resp.status_code, 401)

        # DELETE
        resp = self.delete('/users/', authenticate=False)
        nose.eq_(resp.status_code, 401)

    # Authorized
    def test_user_base_resource(self):
        resp = self.get('/users/')
        nose.eq_(resp.status_code, 200)

        count = resp.json['item_count']

        user = self.mk_user()
        resp = self.get('/users/')
        nose.eq_(resp.json['item_count'], count + 1)

        user.is_public = False
        self._db.session.add(user)
        self._db.session.commit()

        resp = self.get('/users/')
        nose.eq_(resp.json['item_count'], count)

    def test_myself(self):
        resp = self.get('/users/me/')
        nose.eq_(resp.status_code, 200)

        resp = self.post('/users/me/')
        nose.eq_(resp.status_code, 405)

        resp = self.put('/users/me/')
        nose.eq_(resp.status_code, 405)

        resp = self.delete('/users/me/')
        nose.eq_(resp.status_code, 405)

    def test_nonexistent_url(self):
        resp = self.get('/users/you/')
        nose.eq_(resp.status_code, 404)

    def test_user(self):
        resp = self.get('/users/%s/' % self.user.pk)
        nose.eq_(resp.status_code, 200)

    def test_nonexistent_user(self):
        resp = self.get('/users/123/')
        nose.eq_(resp.status_code, 404)

    def test_user_creation(self):
        resp = self.post('/users/', data=self.get_payload())
        nose.eq_(resp.status_code, 201)

        _resp = self.post('/users/', data=self.get_payload())
        nose.eq_(_resp.status_code, 409)  # Conflict

    def test_user_creation_error(self):
        payload = self.get_payload().update({'email': ''})
        resp = self.post('/users/', data=payload)
        nose.eq_(resp.status_code, 400)  # Bad Request

    def test_user_update(self):
        resp = self.post('/users/', data=self.get_payload())
        nose.eq_(resp.status_code, 201)

        user_url = '/users/%s/' % resp.json['id']
        old_name = resp.json['display_name']

        resp = self.put(user_url, data={'display_name': '%s2' % old_name})
        nose.eq_(resp.status_code, 204)

        resp = self.get(user_url)
        nose.eq_(resp.status_code, 200)
        nose.ok_(resp.json['display_name'] != old_name)

    def test_user_update_error(self):
        resp = self.post('/users/', data=self.get_payload())
        user_url = '/users/%s/' % resp.json['id']

        resp = self.put(user_url, data={'email': ''})
        nose.eq_(resp.status_code, 400)  # Bad Request

    def test_user_update_conflict(self):
        resp = self.post('/users/', data={'email': 'one'})
        resp_url = '/users/%s/' % resp.json['id']

        self.post('/users/', data={'email': 'two'})

        resp = self.put(resp_url, data={'email': 'two'})
        nose.eq_(resp.status_code, 409)  # Conflict

    def test_user_delete(self):
        resp = self.post('/users/', data=self.get_payload())
        nose.eq_(resp.status_code, 201)

        user_url = '/users/%s/' % resp.json['id']

        resp = self.delete(user_url)
        nose.eq_(resp.status_code, 204)

        resp = self.delete(user_url)
        nose.eq_(resp.status_code, 404)
