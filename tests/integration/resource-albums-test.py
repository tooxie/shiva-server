# -*- coding: utf-8 -*-
from flask import json
from nose import tools as nose

from tests.integration.resource import ResourceTestCase


class AlbumResourceTestCase(ResourceTestCase):
    """
    GET /albums [artist=<int>]
        200 OK
        401 Unauthorized
    POST /albums name=<str> [year=<int>] [cover_url=<str>]
        201 Created
        400 Bad Request
        401 Unauthorized
        409 Conflict
    GET /albums/<id> [fulltree=<bool>]
        200 OK
        401 Unauthorized
        404 Not Found
    PUT /albums/<id> [name=<str>] [year=<int>] [cover_url=<str>]
        204 No Content
        400 Bad Request
        401 Unauthorized
        404 Not Found
    DELETE /albums/<id>
        204 No Content
        401 Unauthorized
        404 Not Found
    """

    def get_payload(self):
        return {
            'name': "Keep rockin'",
        }

    def test_album_base_resource(self):
        rv = self.app.get('/albums')
        resp = json.loads(rv.data)

        nose.eq_(rv.status_code, 200)
        nose.ok_(resp.has_key('item_count'))
        nose.ok_(resp.has_key('items'))
        nose.ok_(resp.has_key('page'))
        nose.ok_(resp.has_key('page_size'))
        nose.ok_(resp.has_key('pages'))

    def test_nonexistent_album(self):
        rv = self.app.get('/albums/123')
        nose.eq_(rv.status_code, 404)

    def test_fulltree(self):
        rv = self.app.get('/albums/%s?fulltree=1' % self.album_pk)
        nose.eq_(rv.status_code, 200)

    def test_album_creation(self):
        rv = self.app.post('/albums', data=self.get_payload())
        resp = json.loads(rv.data)

        nose.eq_(rv.status_code, 201)

        _rv = self.app.post('/albums', data=self.get_payload())
        nose.eq_(_rv.status_code, 409)  # Conflict

    def test_album_update(self):
        url = '/albums/%s' % self.album.pk
        old_name = self.album.name

        rv = self.app.put(url, data={'name': 'Rock no more'})
        rv = self.app.get(url)
        resp = json.loads(rv.data)

        nose.ok_(resp['name'] != old_name)

    def test_album_deletion(self):
        rv = self.app.post('/albums', data={'name': 'derp'})
        resp = json.loads(rv.data)

        album_id = resp['id']

        rv = self.app.delete('/albums/%i' % album_id)
        nose.eq_(rv.status_code, 200)

        rv = self.app.get('/albums/%i' % album_id)
        nose.eq_(rv.status_code, 404)
