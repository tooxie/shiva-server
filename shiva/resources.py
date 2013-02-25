# -*- coding: utf-8 -*-
from datetime import datetime
import logging
import urllib2

from flask import request, Response, redirect, current_app as app, g
from flask.ext.restful import abort, fields, marshal, Resource
from lxml import etree
import requests

from shiva.converter import get_converter
from shiva.fields import (Boolean, DownloadURI, ForeignKeyField, InstanceURI,
                          ManyToManyField, TrackFiles)
from shiva.lyrics import get_lyrics
from shiva.models import Artist, Album, Track, Lyrics

logger = logging.getLogger(__name__)

DEFAULT_ALBUM_COVER = ('http://wortraub.com/wp-content/uploads/2012/07/'
                       'Vinyl_Close_Up.jpg')
DEFAULT_ARTIST_IMAGE = 'http://www.super8duncan.com/images/band_silhouette.jpg'


class JSONResponse(Response):
    """
    A subclass of flask.Response that sets the Content-Type header by default
    to "application/json".

    """

    def __init__(self, status=200, **kwargs):
        params = {
            'headers': [],
            'mimetype': 'application/json',
            'response': '',
            'status': status,
        }
        params.update(kwargs)

        super(JSONResponse, self).__init__(**params)


def full_tree():
    """ Checks the GET parameters to see if a full tree was requested. """

    arg = request.args.get('fulltree')

    return (arg and arg not in ('false', '0'))


def paginate(queryset):
    """
    Function that receives a queryset and paginates it based on the GET
    parameters.

    """

    try:
        page_size = int(request.args.get('page_size', 0))
    except ValueError:
        page_size = 0

    try:
        page_number = int(request.args.get('page', 0))
    except ValueError:
        page_number = 0

    if not page_size or not page_number:
        return queryset

    total = queryset.count()

    if total < page_size:
        return queryset

    limit = page_size
    offset = page_size * (page_number - 1)

    return queryset.limit(limit).offset(offset)


class ArtistResource(Resource):
    """
    """

    resource_fields = {
        'id': fields.Integer(attribute='pk'),
        'name': fields.String,
        'slug': fields.String,
        'uri': InstanceURI('artist'),
        'download_uri': DownloadURI('artist'),
        'image': fields.String(default=DEFAULT_ARTIST_IMAGE),
        'events_uri': fields.String(attribute='events'),
    }

    def get(self, artist_id=None, artist_slug=None):
        if not artist_id and not artist_slug:
            return list(self.get_all())

        if not artist_id and artist_slug:
            artist = self.get_by_slug(artist_slug)
        else:
            artist = self.get_one(artist_id)

        if full_tree():
            return self.get_full_tree(artist)

        return marshal(artist, self.resource_fields)

    def get_all(self):
        for artist in paginate(Artist.query.order_by(Artist.name)):
            yield marshal(artist, self.resource_fields)

    def get_one(self, artist_id):
        artist = Artist.query.get(artist_id)

        if not artist:
            return JSONResponse(404)

        return artist

    def get_by_slug(self, artist_slug):
        artist = Artist.query.filter_by(slug=artist_slug).first()

        if not artist:
            return JSONResponse(404)

        return artist

    def get_full_tree(self, artist):
        _artist = marshal(artist, self.resource_fields)
        _artist['albums'] = []

        albums = AlbumResource()

        for album in artist.albums:
            _artist['albums'].append(albums.get_full_tree(album))

        return _artist

    def delete(self, artist_id=None):
        if not artist_id:
            return JSONResponse(405)

        artist = Artist.query.get(artist_id)
        if not artist:
            return JSONResponse(404)

        g.db.session.delete(artist)
        g.db.session.commit()

        return {}


class AlbumResource(Resource):
    """
    """

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

    def get(self, album_id=None, album_slug=None):
        if not album_id and not album_slug:
            return list(self.get_many())

        if not album_id and album_slug:
            album = self.get_by_slug(album_slug)
        else:
            album = self.get_one(album_id)

        if full_tree():
            return self.get_full_tree(album)

        return marshal(album, self.resource_fields)

    def get_many(self):
        artist_pk = request.args.get('artist')
        if artist_pk:
            albums = Album.query.join(Album.artists).filter(
                Artist.pk == artist_pk)
        else:
            albums = Album.query

        queryset = albums.order_by(Album.year, Album.name, Album.pk)
        for album in paginate(queryset):
            yield marshal(album, self.resource_fields)

    def get_one(self, album_id):
        album = Album.query.get(album_id)

        if not album:
            abort(404)

        return album

    def get_by_slug(self, album_slug):
        album = Album.query.filter_by(slug=album_slug).first()

        if not album:
            abort(404)

        return album

    def get_full_tree(self, album):
        _album = marshal(album, self.resource_fields)
        _album['tracks'] = []

        tracks = TracksResource()

        for track in album.tracks.order_by('number', 'title'):
            _album['tracks'].append(tracks.get_full_tree(track))

        return _album

    def delete(self, album_id=None):
        if not album_id:
            return JSONResponse(405)

        album = Album.query.get(album_id)
        if not album:
            return JSONResponse(404)

        g.db.session.delete(album)
        g.db.session.commit()

        return {}


class TracksResource(Resource):
    """
    """

    resource_fields = {
        'id': fields.Integer(attribute='pk'),
        'uri': InstanceURI('track'),
        'files': TrackFiles,
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

    def get(self, track_id=None, track_slug=None):
        if not track_id and not track_slug:
            return list(self.get_many())

        if not track_id and track_slug:
            track = self.get_by_slug(track_slug)
        else:
            track = self.get_one(track_id)

        if full_tree():
            return self.get_full_tree(track, include_scraped=True)

        return marshal(track, self.resource_fields)

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

        queryset = tracks.order_by(Track.album_pk, Track.number, Track.pk)
        for track in paginate(queryset):
            yield marshal(track, self.resource_fields)

    def get_one(self, track_id):
        track = Track.query.get(track_id)

        if not track:
            abort(404)

        return track

    def get_by_slug(self, track_slug):
        track = Track.query.filter_by(slug=track_slug).first()

        if not track:
            abort(404)

        return track

    def get_full_tree(self, track, include_scraped=False):
        """
        Retrives the full tree for a track. If the include_scraped option is
        not set then a normal track structure will be retrieved. If its set
        external resources that need to be scraped, like lyrics, will also be
        included.

        This is disabled by default to avois DoS'ing lyrics' websites when
        requesting many tracks at once.

        """

        _track = marshal(track, self.resource_fields)

        if include_scraped:
            lyrics = LyricsResource()
            _track['lyrics'] = lyrics.get_for(track)

        # tabs = TabsResource()
        # _track['tabs'] = tabs.get()

        return _track

    def delete(self, track_id=None):
        if not track_id:
            return JSONResponse(405)

        track = Track.query.get(track_id)
        if not track:
            return JSONResponse(404)

        g.db.session.delete(track)
        g.db.session.commit()

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

    def get(self, track_id=None, track_slug=None):
        if not track_id and not track_slug:
            return JSONResponse(404)

        if not track_id and track_slug:
            track = Track.query.filter_by(slug=track_slug).first()
        else:
            track = Track.query.get(track_id)

        return self.get_for(track)

    def get_for(self, track):
        if track.lyrics:
            return marshal(track.lyrics, self.resource_fields)

        try:
            lyrics = get_lyrics(track)
        except Exception, e:
            logging.debug(e)
            lyrics = None

        if not lyrics:
            return JSONResponse(404)

        return marshal(lyrics, self.resource_fields)

    def post(self, track_id):
        text = request.form.get('text', None)
        if not text:
            return JSONResponse(400)

        track = Track.query.get(track_id)
        lyric = Lyrics(track=track, text=text)

        g.db.session.add(lyric)
        g.db.commit()

        return JSONResponse(200)

    def delete(self, track_id):
        track = Track.query.get(track_id)
        g.db.session.delete(track.lyrics)
        g.db.session.commit()

        return JSONResponse(200)


class ConvertResource(Resource):
    """
    """

    def get(self, track_id):
        track = Track.query.get(track_id)
        mimename = request.args.get('mimetype')
        if not track:
            print('no track')
        if not mimename:
            print('no mimename')

        if not track or not mimename:
            return JSONResponse(404)

        converter = get_converter()(track.path)
        mimetype = converter.get_mimetypes().get(mimename)
        if not mimetype:
            print('no mimetype')
        if not mimetype:
            return JSONResponse(404)

        if not converter.exists_for_mimetype(mimetype):
            converter.convert_to(mimetype)

        uri = converter.get_dest_uri(mimetype)
        print(uri)

        return JSONResponse(status=301, headers={'Location': uri})


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
        'venue': fields.Nested({
            'latitude': fields.String,
            'longitude': fields.String,
            'name': fields.String,
        }),
    }

    def get(self, artist_id=None, artist_slug=None):
        if not artist_id and not artist_slug:
            return JSONResponse(404)

        if not artist_id and artist_slug:
            artist = Artist.query.filter_by(slug=artist_slug).first()
        else:
            artist = Artist.query.get(artist_id)

        if not artist:
            return JSONResponse(404)

        latitude = request.args.get('latitude')
        longitude = request.args.get('longitude')

        country = request.args.get('country')
        city = request.args.get('city')

        if latitude and longitude:
            location = (latitude, longitude)
        elif country and city:
            location = (city, country)
        else:
            location = ()

        response = self.fetch(artist.name, location)

        return list(response) if response else []

    def fetch(self, artist_name, location):
        bit_uri = ('http://api.bandsintown.com/artists/%(artist)s/events'
                   '/search?format=json&app_id=%(app_id)s&api_version=2.0')
        bit_uri = bit_uri % {
            'artist': urllib2.quote(artist_name),
            'app_id': app.config['BANDSINTOWN_APP_ID'],
        }

        _location = urllib2.quote('%s, %s' % location) if location else \
                'use_geoip'

        bit_uri = '&'.join((bit_uri, '='.join(('location', _location))))

        logger.info(bit_uri)

        try:
            response = requests.get(bit_uri)
        except requests.exceptions.RequestException:
            return

        for event in response.json():
            yield marshal(ShowModel(artist_name, event), self.resource_fields)


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

        logger.info(mb_uri)

        response = requests.get(mb_uri)
        mb_xml = etree.fromstring(response.text)
        # /root/artist-list/artist.id
        artist_list = mb_xml.getchildren()[0].getchildren()
        if artist_list:
            return artist_list[0].get('id')

        return None

    def __getitem__(self, key):
        return getattr(self, key, None)


class RandomResource(Resource):
    """
    Retrieves a random instance of a specified resource.
    """

    def get(self, resource_name):
        get_resource = getattr(self, 'get_%s' % resource_name)

        if get_resource and callable(get_resource):
            return get_resource()

        return JSONResponse(404)

    def get_random_for(self, model, resource_name):
        from random import random

        top = model.query.count()
        model_id = int(random() * top)
        instance = model.query.get(model_id)
        resource_fields = {
            'id': fields.Integer(attribute='pk'),
            'uri': InstanceURI(resource_name),
        }

        return marshal(instance, resource_fields)

    def get_track(self):
        return self.get_random_for(Track, 'track')

    def get_album(self):
        return self.get_random_for(Album, 'album')

    def get_artist(self):
        return self.get_random_for(Artist, 'artist')


class ClientResource(Resource):
    def get(self):
        clients = [
            {
                'name': 'Shiva-Client',
                'uri': 'https://github.com/tooxie/shiva-client',
                'author': u'Alvaro Mouriño <alvaro@mourino.net>',
            },
        ]

        return clients
