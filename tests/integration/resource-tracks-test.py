# -*- coding: utf-8 -*-
from cStringIO import StringIO

from nose import tools as nose
from flask import json

from tests.integration.resource import ResourceTestCase


class TrackResourceTestCase(ResourceTestCase):

    def get_payload(self):
        return {
            'title': 'I want it that way',
            'path': '/some/path',
            'track': (StringIO('The content of the mp3'), 'track.mp3'),
            'hash_file': False,
            'no_metadata': True,
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
        rv = self.app.post('/tracks', data=self.get_payload(),
                           content_type='multipart/form-data')

        resp = json.loads(rv.data)

        nose.eq_(rv.status_code, 201)

        _rv = self.app.post('/tracks', data=self.get_payload())
        nose.eq_(_rv.status_code, 409)  # Conflict

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
