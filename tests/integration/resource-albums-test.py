# -*- coding: utf-8 -*-
from nose import tools as nose

from flask import json

from tests.integration.resource import ResourceTestCase


class AlbumResourceTestCase(ResourceTestCase):

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

    def test_album_creation(self):
        rv = self.app.post('/albums', data=self.get_payload())
        resp = json.loads(rv.data)

        nose.eq_(rv.status_code, 201)

        _rv = self.app.post('/albums', data=self.get_payload())
        nose.eq_(_rv.status_code, 409)  # Conflict

    def test_album_deletion(self):
        rv = self.app.delete('/albums/%i' % self.album.pk)
        nose.eq_(rv.status_code, 200)

        rv = self.app.get('/albums/%i' % self.album.pk)
        nose.eq_(rv.status_code, 404)
