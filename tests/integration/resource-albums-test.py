# -*- coding: utf-8 -*-
from nose import tools as nose

from .resource import ResourceTestCase


class AlbumResourceTestCase(ResourceTestCase):
    """
    GET /albums/ [artist=<int>]
        200 OK
        401 Unauthorized
    POST /albums/ name=<str> [year=<int>] [cover_url=<str>]
        201 Created
        400 Bad Request
        401 Unauthorized
    GET /albums/<id>/ [fulltree=<bool>]
        200 OK
        401 Unauthorized
        404 Not Found
    PUT /albums/<id>/ [name=<str>] [year=<int>] [cover_url=<str>]
        204 No Content
        400 Bad Request
        401 Unauthorized
        404 Not Found
    DELETE /albums/<id>/
        204 No Content
        401 Unauthorized
        404 Not Found
    """

    def get_payload(self):
        return {
            'name': "Keep rockin'",
        }

    # Unauthorized
    def test_unauthorized_access(self):
        resp = self.get('/albums/', authenticate=False)
        nose.ok_(resp.status_code, 401)

        resp = self.get('/albums/1/', authenticate=False)
        nose.ok_(resp.status_code, 401)

        # POST
        payload = self.get_payload()
        resp = self.post('/albums/', data=payload, authenticate=False)
        nose.ok_(resp.status_code, 401)

        # PUT
        payload = self.get_payload()
        resp = self.put('/albums/1/', data=payload, authenticate=False)
        nose.ok_(resp.status_code, 401)

        # DELETE
        resp = self.delete('/albums/1/', authenticate=False)
        nose.ok_(resp.status_code, 401)

    # Authorized
    def test_album_base_resource(self):
        resp = self.get('/albums/')

        nose.eq_(resp.status_code, 200)
        nose.ok_(resp.json.has_key('item_count'))
        nose.ok_(resp.json.has_key('items'))
        nose.ok_(resp.json.has_key('page'))
        nose.ok_(resp.json.has_key('page_size'))
        nose.ok_(resp.json.has_key('pages'))

    def test_nonexistent_album(self):
        resp = self.get('/albums/123/')
        nose.eq_(resp.status_code, 404)

    def test_fulltree(self):
        resp = self.get('/albums/%s/?fulltree=1' % self.album_pk)
        nose.eq_(resp.status_code, 200)

    def test_album_creation(self):
        resp = self.post('/albums/', data=self.get_payload())
        nose.eq_(resp.status_code, 201)

        _resp = self.post('/albums/', data=self.get_payload())
        # Albums with the same name for the same artist are allowed.
        nose.eq_(_resp.status_code, 201)

        _resp = self.post('/albums/', data={'name': ''})
        # But albums without name are not allowed.
        nose.eq_(_resp.status_code, 400)

    def test_album_update(self):
        url = '/albums/%s/' % self.album.pk
        old_name = self.album.name

        resp = self.put(url, data={'name': 'Rock no more'})
        nose.ok_(resp.status_code, 204)

        resp = self.get(url)
        nose.ok_(resp.status_code, 200)
        nose.ok_(resp.json['name'] != old_name)

        resp = self.put(url, data={'name': ''})
        nose.ok_(resp.status_code, 400)

    def test_album_delete(self):
        resp = self.post('/albums/', data={'name': 'derp'})
        nose.eq_(resp.status_code, 201)

        album_url = '/albums/%s/' % resp.json['id']

        resp = self.delete(album_url)
        nose.eq_(resp.status_code, 204)

        resp = self.get(album_url)
        nose.eq_(resp.status_code, 404)

        resp = self.delete(album_url)
        nose.eq_(resp.status_code, 404)
