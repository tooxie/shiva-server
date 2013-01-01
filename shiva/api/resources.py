# -*- coding: utf-8 -*-
import urllib2

import requests
from flask import request, Response
from flask.ext.restful import abort, fields, marshal, marshal_with, Resource

from shiva.api.fields import (AlbumCover, DownloadURI, FieldMap,
                              ForeignKeyField, InstanceURI, ManyToManyField)
from shiva.api.models import Artist, Album, Track


class JSONResponse(Response):
    def __init__(self, status=200, **kwargs):
        params = {
            'headers': [],
            'mimetype': 'application/json',
            'response': '',
            'status': status,
        }
        params.update(kwargs)

        super(JSONResponse, self).__init__(**params)


class ArtistResource(Resource):
    """
    """

    route_base = 'artists'
    resource_fields = {
        'id': FieldMap('pk', lambda x: int(x)),
        'name': fields.String,
        'uri': InstanceURI('artist'),
        'download_uri': DownloadURI('artist'),
        'image': fields.String,
        'slug': fields.String,
    }

    def get(self, artist_id=None):
        if not artist_id:
            return list(self.get_all())

        return self.get_one(artist_id)

    def get_all(self):
        for artist in Artist.query.order_by(Artist.name):
            yield marshal(artist, self.resource_fields)

    def get_one(self, artist_id):
        artist = Artist.query.get(artist_id)

        if not artist:
            return JSONResponse(404)

        return marshal(artist, self.resource_fields)

    def post(self, artist_id=None):
        if artist_id:
            return JSONResponse(405)

        # artist = new Artist(name=request.form.get('name'))
        # artist.save()

        return JSONResponse(201, headers=[('Location', '/artist/1337')])

    def put(self, artist_id=None):
        if not artist_id:
            return JSONResponse(405)

        return {}

    def delete(self, artist_id=None):
        if not artist_id:
            return JSONResponse(405)

        artist = Artist.query.get(artist_id)
        if not artist:
            return JSONResponse(404)

        db.session.delete(artist)
        db.session.commit()

        return {}


class AlbumResource(Resource):
    """
    """

    route_base = 'albums'
    resource_fields = {
        'id': FieldMap('pk', lambda x: int(x)),
        'name': fields.String,
        'slug': fields.String,
        'year': fields.Integer,
        'uri': InstanceURI('album'),
        'artists': ManyToManyField(Artist, {
            'id': FieldMap('pk', lambda x: int(x)),
            'uri': InstanceURI('artist'),
        }),
        'download_uri': DownloadURI('album'),
        'cover': AlbumCover,
    }

    def get(self, album_id=None):
        if not album_id:
            return list(self.get_many())

        return self.get_one(album_id)

    def get_many(self):
        artist_pk = request.args.get('artist')
        if artist_pk:
            albums = Album.query.join(Album.artists).filter(
                Artist.pk == artist_pk)
        else:
            albums = Album.query

        for album in albums.order_by(Album.year, Album.name, Album.pk):
            yield marshal(album, self.resource_fields)

    @marshal_with(resource_fields)
    def get_one(self, album_id):
        album = Album.query.get(album_id)

        if not album:
            abort(404)

        return album

    def delete(self, album_id=None):
        if not album_id:
            return JSONResponse(405)

        album = Album.query.get(album_id)
        if not album:
            return JSONResponse(404)

        db.session.delete(album)
        db.session.commit()

        return {}


class TracksResource(Resource):
    """
    """

    route_base = 'tracks'
    resource_fields = {
        'id': FieldMap('pk', lambda x: int(x)),
        'uri': InstanceURI('track'),
        'download_uri': DownloadURI('track'),
        'bitrate': fields.Integer,
        'length': fields.Integer,
        'title': fields.String,
        'slug': fields.String,
        'artist': ForeignKeyField(Album, {
            'id': FieldMap('pk', lambda x: int(x)),
            'uri': InstanceURI('artist'),
        }),
        'album': ForeignKeyField(Album, {
            'id': FieldMap('pk', lambda x: int(x)),
            'uri': InstanceURI('album'),
        }),
        'number': fields.Integer,
    }

    def get(self, track_id=None):
        if not track_id:
            return list(self.get_many())

        return self.get_one(track_id)

    # TODO: Pagination
    def get_many(self):
        album_pk = request.args.get('album')
        artist_pk = request.args.get('artist')
        if album_pk:
            album_pk = None if album_pk == 'null' else album_pk
            tracks = Track.query.filter_by(album_pk=album_pk)
        elif artist_pk:
            tracks = Track.query.filter(Track.artist_pk == artist_pk)
        else:
            tracks = Track.query

        for track in tracks.order_by(Track.album_pk, Track.number, Track.pk):
            yield marshal(track, self.resource_fields)

    @marshal_with(resource_fields)
    def get_one(self, track_id):
        track = Track.query.get(track_id)

        if not track:
            abort(404)

        return track

    def delete(self, track_id=None):
        if not track_id:
            return JSONResponse(405)

        track = Track.query.get(track_id)
        if not track:
            return JSONResponse(404)

        db.session.delete(track)
        db.session.commit()

        return {}


class LyricsResource(Resource):
    """
    """

    def get(self, track_id):
        track = Track.query.get(track_id)
        lyricswiki = ('http://lyrics.wikia.com/api.php?'
                      'artist=%(artist)s&song=%(track)s&fmt=realjson')
        print(lyricswiki % {
            'artist': urllib2.quote(track.artist.name),
            'track': urllib2.quote(track.title),
        })
        response = requests.get(lyricswiki % {
            'artist': urllib2.quote(track.artist.name),
            'track': urllib2.quote(track.title),
        })
        lyrics = response.json().get('lyrics')
        if lyrics != "Not found":
            return {
                'lyrics': lyrics,
                'uri': response.json().get('url'),
                'artist': {
                    'id': track.artist.pk,
                    'uri': '/artist/%i' % track.artist.pk,
                },
                'track': {
                    'id': track.pk,
                    'uri': '/track/%i' % track.pk,
                },
            }

        return JSONResponse(404)


class ShowsResource(Resource):
    """
    """

    def get(self, artist_id):
        bit_uri = ('http://api.bandsintown.com/artists/%(artist)s/events.json?'
                   'api_version=2.0&app_id=MY_APP_ID&location=%(location)s')
        artist = Artist.query.get(artist_id)

        if not artist:
            return JSONResponse(404)

        print(bit_uri % {
            'artist': urllib2.quote(artist.name),
            'location': urllib2.quote('Berlin, Germany'),
        })
        response = requests.get(bit_uri % {
            'artist': urllib2.quote(artist.name),
            'location': urllib2.quote('Berlin, Germany'),
        })

        return JSONResponse(response=response.text,
                            status=response.status_code)
