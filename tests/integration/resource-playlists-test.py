# -*- coding: utf-8 -*-
from flask import json
from nose import tools as nose

from .resource import ResourceTestCase


class PlaylistsResourceTestCase(ResourceTestCase):
    """
    GET /playlists/ [user=<int>] [track=<int>]
        200 OK
        401 Unauthorized
    POST /playlists/ name=<str>
        201 Created
        400 Bad Request
        401 Unauthorized
    GET /playlists/<id>/
        200 OK
        401 Unauthorized
        404 Not Found
    PUT /playlists/<id>/ name=<str>
        204 No Content
        401 Unauthorized
        404 Not Found
    POST /playlists/<id>/add/ track=<int> [index=<int>]
        204 No Content
        400 Bad Request
        401 Unauthorized
        404 Not Found
    POST /playlists/<id>/remove/ index=<int>
        204 No Content
        400 Bad Request
        401 Unauthorized
        404 Not Found
    DELETE /playlists/
        204 No Content
        401 Unauthorized
        404 Not Found
    """

    def get_payload(self):
        return {
            'name': 'Playtest',
        }

    # Unauthorized
    def test_unauthorized_access(self):
        resp = self.get('/playlists/', authenticate=False)
        nose.eq_(resp.status_code, 401)

        resp = self.get('/playlists/1/', authenticate=False)
        nose.eq_(resp.status_code, 401)

        # POST
        payload = self.get_payload()
        resp = self.post('/playlists/', data=payload, authenticate=False)
        nose.eq_(resp.status_code, 401)

        # PUT
        resp = self.put('/playlists/', data=payload, authenticate=False)
        nose.eq_(resp.status_code, 401)

        # DELETE
        resp = self.delete('/playlists/', authenticate=False)
        nose.eq_(resp.status_code, 401)

        # POST to /add/
        payload = dict(track=1)
        resp = self.post('/playlists/1/add/', data=payload, authenticate=False)
        nose.eq_(resp.status_code, 401)

        # POST to /remove/
        resp = self.post('/playlists/1/remove/', data=payload,
                         authenticate=False)
        nose.eq_(resp.status_code, 401)

    # Authorized
    def test_playlist_base_resource(self):
        resp = self.get('/playlists/')
        nose.eq_(resp.status_code, 200)

    def test_nonexistent_playlist(self):
        resp = self.get('/playlists/123/')
        nose.eq_(resp.status_code, 404)

    def test_playlist_creation(self):
        resp = self.post('/playlists/', data=self.get_payload())
        nose.eq_(resp.status_code, 201)

    def test_playlist(self):
        resp = self.post('/playlists/', data=self.get_payload())
        playlist_url = '/playlists/%s/' % resp.json['id']
        _resp = self.get(playlist_url)
        nose.eq_(_resp.status_code, 200)
        nose.ok_(_resp.json.has_key('id'))
        nose.ok_(_resp.json.has_key('name'))
        nose.ok_(_resp.json.has_key('user'))
        nose.ok_(_resp.json.has_key('length'))
        nose.ok_(_resp.json.has_key('tracks'))
        nose.ok_(_resp.json.has_key('read_only'))
        nose.ok_(_resp.json.has_key('creation_date'))

    def test_playlist_creation_error(self):
        resp = self.post('/playlists/', data={'name': ''})
        nose.eq_(resp.status_code, 400)

        self._app.config['ALLOW_ANONYMOUS_ACCESS'] = True
        resp = self.post('/playlists/', data={'name': 'Mane'})
        # A logged in user is required for playlist creation.
        nose.eq_(resp.status_code, 400)

    def test_playlist_update(self):
        resp = self.post('/playlists/', data=self.get_payload())
        playlist_url = '/playlists/%s/' % resp.json['id']
        old_name = resp.json['name']
        payload = {'name': '%s-2' % old_name}

        _resp = self.put(playlist_url, data=payload)
        nose.eq_(_resp.status_code, 204)

        _resp = self.get(playlist_url)
        nose.eq_(_resp.json['name'], '%s-2' % old_name)

        # Playlist raise no error on update. If no attribute is set, nothing
        # happens.

    def test_track_addition(self):
        resp = self.post('/playlists/', data=self.get_payload())
        playlist_url = '/playlists/%s/' % resp.json['id']
        add_url = '%sadd/' % playlist_url

        resp = self.post(add_url, data={'track': self.track.pk, 'index': 0})
        nose.eq_(resp.status_code, 204)

        resp = self.post(add_url, data={'track': self.track.pk, 'index': 1})
        nose.eq_(resp.status_code, 204)

        resp = self.post(add_url, data={'track': self.track.pk, 'index': 0})
        nose.eq_(resp.status_code, 204)

        resp = self.post(add_url, data={'track': self.track.pk, 'index': 2})
        nose.eq_(resp.status_code, 204)

        resp = self.post(add_url, data={'track': self.track.pk, 'index': 0})
        nose.eq_(resp.status_code, 204)

        resp = self.get(playlist_url)
        track = resp.json['tracks'][0]
        nose.eq_(len(resp.json['tracks']), 5)
        nose.ok_(track.has_key('id'))
        nose.ok_(track.has_key('uri'))
        nose.ok_(track.has_key('index'))

    def test_track_addition_error(self):
        resp = self.post('/playlists/', data=self.get_payload())
        add_url = '/playlists/%s/add/' % resp.json['id']

        _resp = self.post(add_url, data={})
        nose.eq_(_resp.status_code, 400)

        _resp = self.post(add_url, data={'track': self.track.pk, 'index': 123})
        nose.eq_(_resp.status_code, 400)

    def test_track_addition_to_nonexistent_playlist(self):
        url = '/playlists/123/add/'
        resp = self.post(url, data=self.get_payload())
        nose.eq_(resp.status_code, 404)

    def test_track_removal(self):
        resp = self.post('/playlists/', data=self.get_payload())
        add_url = '/playlists/%s/add/' % resp.json['id']
        remove_url = '/playlists/%s/remove/' % resp.json['id']

        resp = self.post(add_url, data={'track': self.track.pk, 'index': 0})

        resp = self.post(remove_url, data={'index': 0})
        nose.eq_(resp.status_code, 204)

    def test_track_removal_error(self):
        resp = self.post('/playlists/', data=self.get_payload())
        remove_url = '/playlists/%s/remove/' % resp.json['id']

        resp = self.post(remove_url, data={})
        nose.eq_(resp.status_code, 400)

        resp = self.post(remove_url, data={'index': 0})
        nose.eq_(resp.status_code, 400)

    def test_track_removal_from_nonexistent_playlist(self):
        url = '/playlists/123/remove/'
        resp = self.post(url, data={'index': 0})
        nose.eq_(resp.status_code, 404)

    def test_playlist_delete(self):
        resp = self.post('/playlists/', data=self.get_payload())
        playlist_url = '/playlists/%s/' % resp.json['id']

        resp = self.delete(playlist_url)
        nose.eq_(resp.status_code, 204)

        resp = self.get(playlist_url)
        nose.eq_(resp.status_code, 404)

    def test_delete_nonexistent_playlist(self):
        resp = self.delete('/playlists/123/')
        nose.eq_(resp.status_code, 404)

    def test_track_removal(self):
        """
        1. Create playlist
        2. Add existing track
        3. Delete track from DB
        4. Check that the playlists get updated and track is no longer present

        """

        resp = self.post('/playlists/', data=self.get_payload())
        nose.eq_(resp.status_code, 201)
        playlist_url = '/playlists/%s/' % resp.json['id']
        add_url = '/playlists/%s/add/' % resp.json['id']

        track = self.mk_track()
        resp = self.post(add_url, data={'track': track.pk, 'index': 0})
        nose.eq_(resp.status_code, 204)

        resp = self.delete('/tracks/%s/' % track.pk)
        nose.eq_(resp.status_code, 204)

        resp = self.get(playlist_url)
        nose.eq_(resp.json['length'], 0)
