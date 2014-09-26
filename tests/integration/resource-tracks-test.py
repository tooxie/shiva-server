# -*- coding: utf-8 -*-
from cStringIO import StringIO

from flask import json
from nose import tools as nose

from tests.integration.resource import ResourceTestCase


class TrackResourceTestCase(ResourceTestCase):
    """
    GET /tracks [album=<id>] [artist=<id>]
        200 OK
        401 Unauthorized
    POST /tracks track=<file> [title=<str>] [ordinal=<int>] [artist=<int>]
                 [album=<int>]
        201 Created
        400 Bad Request
        401 Unauthorized
        409 Conflict
    GET /tracks/<id> [artist=<int>] [album=<int>]
        200 OK
        401 Unauthorized
        404 Not Found
    PUT /tracks/<id> [title=<str>] [ordinal=<int>] [artist=<int>] [album=<int>]
        204 No Content
        400 Bad Request
        401 Unauthorized
        404 Not Found
    DELETE /tracks/<id>
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

    def test_track_base_resource(self):
        rv = self.app.get('/tracks')
        resp = json.loads(rv.data)

        nose.eq_(rv.status_code, 200)
        nose.ok_(resp.has_key('item_count'))
        nose.ok_(resp.has_key('items'))
        nose.ok_(resp.has_key('page'))
        nose.ok_(resp.has_key('page_size'))
        nose.ok_(resp.has_key('pages'))

    def test_nonexistent_track(self):
        rv = self.app.get('/tracks/123')
        nose.eq_(rv.status_code, 404)

    def test_track_creation(self):
        url = '/tracks?hash_file=false&no_metadata=true'
        rv = self.app.post(url, data=self.get_payload(),
                           content_type='multipart/form-data')

        resp = json.loads(rv.data)

        nose.eq_(rv.status_code, 201)

        _rv = self.app.post(url, data=self.get_payload())
        nose.eq_(_rv.status_code, 409)  # Conflict

    def test_track_creation_with_nonexistent_artist_id(self):
        url = '/tracks?hash_file=false&no_metadata=true'
        payload = self.get_payload()
        payload['artist_id'] = 404
        rv = self.app.post(url, data=payload,
                           content_type='multipart/form-data')

        resp = json.loads(rv.data)

        nose.eq_(rv.status_code, 400)  # Bad Request

    def test_track_creation_with_nonexistent_album_id(self):
        url = '/tracks?hash_file=false&no_metadata=true'
        payload = self.get_payload()
        payload['album_id'] = 404
        rv = self.app.post(url, data=payload,
                           content_type='multipart/form-data')

        resp = json.loads(rv.data)

        nose.eq_(rv.status_code, 400)  # Bad Request

    def test_track_update(self):
        url = '/tracks/%s' % self.track.pk
        old_title = self.track.title

        rv = self.app.put(url, data={'title': 'Downfall'})
        rv = self.app.get(url)
        resp = json.loads(rv.data)

        nose.ok_(resp['title'] != old_title)

    def test_track_deletion(self):
        # TODO: Test ALLOW_DELETE=False
        rv = self.app.delete('/tracks/%i' % self.track.pk)
        nose.eq_(rv.status_code, 200)

        rv = self.app.get('/tracks/%i' % self.track.pk)
        nose.eq_(rv.status_code, 404)
