# -*- coding: utf-8 -*-
import urllib2
from datetime import datetime

from lxml import etree
import requests
from flask import request, Response
from flask.ext.restful import abort, fields, marshal, marshal_with, Resource

from shiva.api.fields import (Boolean, DownloadURI, ForeignKeyField,
                              InstanceURI, ManyToManyField)
from shiva.api.models import Artist, Album, Track
from shiva.api.lyrics import get_lyrics

DEFAULT_ALBUM_COVER = ('http://wortraub.com/wp-content/uploads/2012/07/'
                       'Vinyl_Close_Up.jpg')
DEFAULT_ARTIST_IMAGE = 'http://www.super8duncan.com/images/band_silhouette.jpg'


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
        'id': fields.Integer(attribute='pk'),
        'name': fields.String,
        'slug': fields.String,
        'uri': InstanceURI('artist'),
        'download_uri': DownloadURI('artist'),
        'image': fields.String(default=DEFAULT_ARTIST_IMAGE),
        'events_uri': fields.String(attribute='events'),
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
        'id': fields.Integer(attribute='pk'),
        'name': fields.String,
        'slug': fields.String,
        'year': fields.Integer,
        'uri': InstanceURI('album'),
        'artists': ManyToManyField(Artist, {
            'id': fields.Integer(attribute='pk'),
            'uri': InstanceURI('artist'),
        }),
        'download_uri': DownloadURI('album'),
        'cover': fields.String(default=DEFAULT_ALBUM_COVER),
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
        'id': fields.Integer(attribute='pk'),
        'uri': InstanceURI('track'),
        'download_uri': DownloadURI('track'),
        'bitrate': fields.Integer,
        'length': fields.Integer,
        'title': fields.String,
        'slug': fields.String,
        'artist': ForeignKeyField(Artist, {
            'id': fields.Integer(attribute='pk'),
            'uri': InstanceURI('artist'),
        }),
        'album': ForeignKeyField(Album, {
            'id': fields.Integer(attribute='pk'),
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

    resource_fields = {
        'id': fields.Integer(attribute='pk'),
        'uri': InstanceURI('lyrics'),
        'text': fields.String,
        'source_uri': fields.String(attribute='source'),
        'track': ForeignKeyField(Track, {
            'id': fields.Integer(attribute='pk'),
            'uri': InstanceURI('track'),
        }),
    }

    def get(self, track_id):
        track = Track.query.get(track_id)
        if track.lyrics:
            return marshal(track.lyrics, self.resource_fields)

        lyrics = get_lyrics(track)

        if not lyrics:
            return JSONResponse(404)

        return marshal(lyrics, self.resource_fields)


class ShowsResource(Resource):
    """
    """

    resource_fields = {
        'id': fields.String,
        'artists': ManyToManyField(Artist, {
            'id': fields.Integer(attribute='pk'),
            'uri': InstanceURI('artist'),
        }),
        'other_artists': fields.List(fields.Raw),
        'datetime': fields.DateTime,
        'title': fields.String,
        'tickets_left': Boolean,
        'tickets_uri': fields.String,
        'venue': fields.Nested({
            'latitude': fields.String,
            'longitude': fields.String,
            'name': fields.String,
        }),
    }

    def get(self, artist_id, latitude=None, longitude=None):
        artist = Artist.query.get(artist_id)

        if not artist:
            return JSONResponse(404)

        return list(self.fetch(artist.name, latitude, longitude))

    def fetch(self, artist, latitude, longitude):
        bit_uri = ('http://api.bandsintown.com/artists/%(artist)s/events.json?'
                   'api_version=2.0&app_id=MY_APP_ID&location=%(location)s')
        bit_uri = bit_uri % {
            'artist': urllib2.quote(artist),
            'location': urllib2.quote('%s, %s' % (latitude, longitude))}

        response = requests.get(bit_uri)

        for event in response.json():
            yield marshal(ShowModel(artist, event), self.resource_fields)


class ShowModel(object):
    """
    Mock model that encapsulates the show logic for converting a JSON structure
    into an object.

    """

    def __init__(self, artist, json):
        self.json = json
        self.id = json['id']
        self.artists, self.other_artists = self.split_artists(json['artists'])
        self.datetime = self.to_datetime(json['datetime'])
        self.title = json['title']
        self.tickets_left = (json['ticket_status'] == 'available')
        self.tickets_uri = json['ticket_url']
        self.venue = json['venue']

    def split_artists(self, json):
        if len(json) == 0:
            ([], [])
        elif len(json) == 1:
            artist = Artist.query.filter_by(name=json[0]['name']).first()

            return ([artist], [])

        my_artists = []
        other_artists = []
        for artist_dict in json:
            artist = Artist.query.filter_by(name=artist_dict['name'])
            if artist.count():
                my_artists.append(artist.first())
            else:
                del artist_dict['thumb_url']
                other_artists.append(artist_dict)

        return (my_artists, other_artists)

    def to_datetime(self, timestamp):
        return datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S')

    def get_mbid(self, artist):
        mb_uri = 'http://musicbrainz.org/ws/2/artist?query=%(artist)s' % {
            'artist': urllib2.quote(artist)
        }
        response = requests.get(mb_uri)
        mb_xml = etree.fromstring(response.text)
        # /root/artist-list/artist.id
        artist_list = mb_xml.getchildren()[0].getchildren()
        if artist_list:
            return artist_list[0].get('id')

        return None

    def __getitem__(self, key):
        return getattr(self, key, None)
