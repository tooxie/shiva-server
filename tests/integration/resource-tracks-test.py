# -*- coding: utf-8 -*-
from cStringIO import StringIO

from nose import tools as nose

from .resource import ResourceTestCase


class TrackResourceTestCase(ResourceTestCase):
    """
    GET /tracks/ [album=<id>] [artist=<id>]
        200 OK
        401 Unauthorized
    POST /tracks/ track=<file> [title=<str>] [ordinal=<int>] [artist=<int>]
                 [album=<int>]
        201 Created
        400 Bad Request
        401 Unauthorized
        409 Conflict
    GET /tracks/<id>/ [artist=<int>] [album=<int>]
        200 OK
        401 Unauthorized
        404 Not Found
    PUT /tracks/<id>/ [title=<str>] [ordinal=<int>] [artist=<int>]
                      [album=<int>]
        204 No Content
        400 Bad Request
        401 Unauthorized
        404 Not Found
    DELETE /tracks/<id>/
        204 No Content
        401 Unauthorized
        404 Not Found
    """

    def get_payload(self):
        return {
            'title': 'I want it that way',
            'path': '/some/path',
            'track': (StringIO('The content of the mp3'), 'track.mp3'),
        }

    # Unauthorized
    def test_unauthorized_track_base_resource(self):
        resp = self.get('/tracks/', authenticate=False)
        nose.eq_(resp.status_code, 401)

        resp = self.get('/tracks/1/', authenticate=False)
        nose.eq_(resp.status_code, 401)

        # POST
        payload = self.get_payload()
        resp = self.post('/tracks/', data=payload, authenticate=False)
        nose.eq_(resp.status_code, 401)

        # PUT
        payload = self.get_payload()
        resp = self.put('/tracks/', data=payload, authenticate=False)
        nose.eq_(resp.status_code, 401)

        # DELETE
        resp = self.delete('/tracks/', authenticate=False)
        nose.eq_(resp.status_code, 401)

    # Authorized
    def test_track_base_resource(self):
        resp = self.get('/tracks/')

        nose.eq_(resp.status_code, 200)
        nose.ok_(resp.json.has_key('item_count'))
        nose.ok_(resp.json.has_key('items'))
        nose.ok_(resp.json.has_key('page'))
        nose.ok_(resp.json.has_key('page_size'))
        nose.ok_(resp.json.has_key('pages'))

    def test_track(self):
        resp = self.get('/tracks/%s/' % self.track.pk)
        nose.eq_(resp.status_code, 200)

    def test_nonexistent_track(self):
        resp = self.get('/tracks/123/')
        nose.eq_(resp.status_code, 404)

    def test_track_creation(self):
        url = '/tracks/?hash_file=false&no_metadata=true'
        resp = self.post(url, data=self.get_payload(),
                           content_type='multipart/form-data')

        nose.eq_(resp.status_code, 201)

        _resp = self.post(url, data=self.get_payload())
        nose.eq_(_resp.status_code, 409)  # Conflict

    def test_track_creation_error(self):
        resp = self.post('/tracks/', content_type='multipart/form-data')
        nose.eq_(resp.status_code, 400)  # Bad Request

    def test_track_creation_with_nonexistent_artist_id(self):
        url = '/tracks/?hash_file=false&no_metadata=true'
        payload = self.get_payload().update({'album_id': 404})
        resp = self.post(url, data=payload,
                         content_type='multipart/form-data')

        nose.eq_(resp.status_code, 400)  # Bad Request

    def test_track_creation_with_nonexistent_album_id(self):
        url = '/tracks/?hash_file=false&no_metadata=true'
        payload = self.get_payload().update({'album_id': 404})
        resp = self.post(url, data=payload,
                           content_type='multipart/form-data')

        nose.eq_(resp.status_code, 400)  # Bad Request

    def test_track_update(self):
        url = '/tracks/%s/' % self.track.pk
        old_title = self.track.title

        resp = self.put(url, data={'title': 'Downfall'})
        nose.eq_(resp.status_code, 204)

        resp = self.get(url)
        nose.ok_(resp.status_code, 200)
        nose.ok_(resp.json['title'] != old_title)

    # TODO: Test update conflict (409)
    def test_track_update_error(self):
        url = '/tracks/%s/' % self.track.pk
        resp = self.put(url, data={'track': ''})
        nose.eq_(resp.status_code, 400)  # Bad Request

    def test_track_deletion(self):
        # TODO: Test ALLOW_DELETE=False
        url = '/tracks/?hash_file=false&no_metadata=true'
        resp = self.post(url, data=self.get_payload(),
                         content_type='multipart/form-data')
        nose.eq_(resp.status_code, 201)

        track_url = '/tracks/%s/' % resp.json['id']

        resp = self.delete(track_url)
        nose.eq_(resp.status_code, 204)

        resp = self.get(track_url)
        nose.eq_(resp.status_code, 404)

        resp = self.delete(track_url)
        nose.eq_(resp.status_code, 404)
