# -*- coding: utf-8 -*-
from nose import tools as nose

from .resource import ResourceTestCase


class ArtistResourceTestCase(ResourceTestCase):
    """
    GET /artists/
        200 OK
        401 Unauthorized
    POST /artists/ name=<str> [image_url=<str>]
        201 Created
        400 Bad Request
        401 Unauthorized
        409 Conflict
    GET /artists/<id>/ [fulltree=<bool>]
        200 OK
        401 Unauthorized
        404 Not Found
    PUT /artists/<id>/ [name=<str>] [image_url=<str>]
        204 No Content
        400 Bad Request
        401 Unauthorized
        404 Not Found
    DELETE /artists/<id>/
        204 No Content
        401 Unauthorized
        404 Not Found
    """

    def get_payload(self):
        return {
            'name': 'Flip',
        }

    # Unauthorized
    def test_unauthorized_access(self):
        resp = self.get('/artists/', authenticate=False)
        nose.eq_(resp.status_code, 401)

        resp = self.get('/artists/1/', authenticate=False)
        nose.eq_(resp.status_code, 401)

        # POST
        payload = self.get_payload()
        resp = self.post('/artists/', data=payload, authenticate=False)
        nose.eq_(resp.status_code, 401)

        # PUT
        payload = self.get_payload()
        resp = self.put('/artists/', data=payload, authenticate=False)
        nose.eq_(resp.status_code, 401)

        # DELETE
        resp = self.delete('/artists/', authenticate=False)
        nose.eq_(resp.status_code, 401)

    # Authorized
    def test_artist_base_resource(self):
        resp = self.get('/artists/')

        nose.eq_(resp.status_code, 200)
        nose.ok_(resp.json.has_key('item_count'))
        nose.ok_(resp.json.has_key('items'))
        nose.ok_(resp.json.has_key('page'))
        nose.ok_(resp.json.has_key('page_size'))
        nose.ok_(resp.json.has_key('pages'))

    def test_artist(self):
        resp = self.get('/artists/%s/' % self.artist.pk)
        nose.eq_(resp.status_code, 200)

    def test_nonexistent_artist(self):
        resp = self.get('/artists/123/')
        nose.eq_(resp.status_code, 404)

    def test_artist_fulltree(self):
        resp = self.get('/artists/%s/?fulltree=1' % self.artist.pk)
        nose.eq_(resp.status_code, 200)
        nose.ok_(resp.json.has_key('albums'))

    def test_artist_creation(self):
        resp = self.post('/artists/', data=self.get_payload())
        nose.eq_(resp.status_code, 201)

        _resp = self.post('/artists/', data=self.get_payload())
        nose.eq_(_resp.status_code, 409)  # Conflict

    def test_artist_creation_error(self):
        resp = self.post('/artists/', data=self.get_payload())
        nose.eq_(resp.status_code, 201)

        _resp = self.post('/artists/', data={'name': ''})
        nose.eq_(_resp.status_code, 400)  # Bad Request

    def test_artist_update(self):
        url = '/artists/%s/' % self.artist.pk
        old_name = self.artist.name

        resp = self.put(url, data={'name': '1on4'})
        nose.eq_(resp.status_code, 204)

        resp = self.get(url)
        nose.ok_(resp.status_code, 200)
        nose.ok_(resp.json['name'] != old_name)

    def test_artist_update_error(self):
        url = '/artists/%s/' % self.artist.pk
        resp = self.put(url, data={'name': ''})
        nose.eq_(resp.status_code, 400)

    def test_artist_deletion(self):
        resp = self.post('/artists/', data=self.get_payload())
        nose.eq_(resp.status_code, 201)

        artist_url = '/artists/%s/' % resp.json['id']

        resp = self.delete(artist_url)
        nose.eq_(resp.status_code, 204)

        resp = self.get(artist_url)
        nose.eq_(resp.status_code, 404)

        resp = self.delete(artist_url)
        nose.eq_(resp.status_code, 404)
