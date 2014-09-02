# -*- coding: utf-8 -*-
from nose import tools as nose

from flask import json

from tests.integration.resource import ResourceTestCase


class ArtistResourceTestCase(ResourceTestCase):

    def get_payload(self):
        return {
            'name': 'Flip',
        }

    def test_artist_base_resource(self):
        rv = self.app.get('/artists')
        resp = json.loads(rv.data)

        nose.eq_(rv.status_code, 200)
        nose.ok_(resp.has_key('item_count'))
        nose.ok_(resp.has_key('items'))
        nose.ok_(resp.has_key('page'))
        nose.ok_(resp.has_key('page_size'))
        nose.ok_(resp.has_key('pages'))

    def test_nonexistent_artist(self):
        rv = self.app.get('/artists/123')
        nose.eq_(rv.status_code, 404)

    def test_artist_creation(self):
        rv = self.app.post('/artists', data=self.get_payload())
        resp = json.loads(rv.data)

        nose.eq_(rv.status_code, 201)

        _rv = self.app.post('/artists', data=self.get_payload())
        nose.eq_(_rv.status_code, 409)  # Conflict

    def test_artist_deletion(self):
        rv = self.app.delete('/artists/%i' % self.artist.pk)
        nose.eq_(rv.status_code, 200)

        rv = self.app.get('/artists/%i' % self.artist.pk)
        nose.eq_(rv.status_code, 404)
