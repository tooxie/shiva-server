# -*- coding: utf-8 -*-
from datetime import datetime
import logging
import urllib2
import traceback

from flask import request, current_app as app, g
from flask.ext.restful import abort, fields, marshal
import requests

from shiva import get_version, get_contributors
from shiva.converter import get_converter
from shiva.exceptions import InvalidMimeTypeError
from shiva.fields import (Boolean, DownloadURI, ForeignKeyField, InstanceURI,
                          ManyToManyField, TrackFiles)
from shiva.http import Resource, JSONResponse
from shiva.lyrics import get_lyrics
from shiva.mocks import ShowModel
from shiva.models import Artist, Album, Track, Lyrics

logger = logging.getLogger(__name__)


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

    def get_resource_fields(self):
        return {
            'id': fields.Integer(attribute='pk'),
            'name': fields.String,
            'slug': fields.String,
            'uri': InstanceURI('artist'),
            'download_uri': DownloadURI('artist'),
            'image': fields.String(default=app.config['DEFAULT_ARTIST_IMAGE']),
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

        return marshal(artist, self.get_resource_fields())

    def get_all(self):
        for artist in paginate(Artist.query.order_by(Artist.name)):
            yield marshal(artist, self.get_resource_fields())

    def get_one(self, artist_id):
        artist = Artist.query.get(artist_id)

        if not artist:
            abort(404)

        return artist

    def get_by_slug(self, artist_slug):
        artist = Artist.query.filter_by(slug=artist_slug).first()

        if not artist:
            abort(404)

        return artist

    def get_full_tree(self, artist):
        _artist = marshal(artist, self.get_resource_fields())
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
            abort(404)

        g.db.session.delete(artist)
        g.db.session.commit()

        return {}


class AlbumResource(Resource):
    """
    """

    def get_resource_fields(self):
        return {
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
            'cover': fields.String(default=app.config['DEFAULT_ALBUM_COVER']),
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

        return marshal(album, self.get_resource_fields())

    def get_many(self):
        artist_pk = request.args.get('artist')
        if artist_pk:
            albums = Album.query.join(Album.artists).filter(
                Artist.pk == artist_pk)
        else:
            albums = Album.query

        queryset = albums.order_by(Album.year, Album.name, Album.pk)
        for album in paginate(queryset):
            yield marshal(album, self.get_resource_fields())

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
        _album = marshal(album, self.get_resource_fields())
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
            abort(404)

        g.db.session.delete(album)
        g.db.session.commit()

        return {}


class TracksResource(Resource):
    """
    """

    def get_resource_fields(self):
        return {
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

        return marshal(track, self.get_resource_fields())

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
            yield marshal(track, self.get_resource_fields())

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

        _track = marshal(track, self.get_resource_fields())

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
            abort(404)

        g.db.session.delete(track)
        g.db.session.commit()

        return {}


class LyricsResource(Resource):
    """
    """

    def get_resource_fields(self):
        return {
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
            abort(404)

        if not track_id and track_slug:
            track = Track.query.filter_by(slug=track_slug).first()
        else:
            track = Track.query.get(track_id)

        return self.get_for(track)

    def get_for(self, track):
        if track.lyrics:
            return marshal(track.lyrics, self.get_resource_fields())

        try:
            lyrics = get_lyrics(track)
        except:
            logging.debug(traceback.format_exc())
            lyrics = None

        if not lyrics:
            abort(404)

        return marshal(lyrics, self.get_resource_fields())

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
        mimetype = request.args.get('mimetype')
        if not track or not mimetype:
            abort(404)

        ConverterClass = get_converter()
        try:
            converter = ConverterClass(track, mimetype=mimetype)
        except InvalidMimeTypeError, e:
            print(e)
            abort(400)

        converter.convert()
        uri = converter.get_uri() or DownloadURI('track').output(None, track)

        return JSONResponse(status=301, headers={'Location': uri})


class ShowsResource(Resource):
    """
    """

    def get_resource_fields(self):
        return {
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
            abort(404)

        if not artist_id and artist_slug:
            artist = Artist.query.filter_by(slug=artist_slug).first()
        else:
            artist = Artist.query.get(artist_id)

        if not artist:
            abort(404)

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
            yield marshal(ShowModel(artist_name, event),
                          self.get_resource_fields())


class RandomResource(Resource):
    """Retrieves a random instance of a specified resource."""

    def get(self, resource_name):
        get_resource = getattr(self, 'get_%s' % resource_name)

        if get_resource and callable(get_resource):
            resource_fields = {
                'id': fields.Integer(attribute='pk'),
                'uri': InstanceURI(resource_name),
            }

            return marshal(get_resource(), resource_fields)

        abort(404)

    def get_track(self):
        return Track.random()

    def get_album(self):
        return Album.random()

    def get_artist(self):
        return Artist.random()


class WhatsNewResource(Resource):
    """
    Resource consisting of artists, albums and tracks that were indexed after a
    given date.

    """

    def get(self):
        news = {'artists': [], 'albums': [], 'tracks': []}
        try:
            self.since = datetime.strptime(request.args.get('since'), '%Y%m%d')
        except:
            print(traceback.format_exc())
            return news

        news = {
            'artists': self.get_new_for(Artist, 'artist'),
            'albums': self.get_new_for(Album, 'album'),
            'tracks': self.get_new_for(Track, 'track'),
        }

        return news

    def get_new_for(self, model, resource_name):
        """
        Fetches all the instances with ``date_added`` older than
        ``self.since``.

        """

        query = model.query.filter(model.date_added > self.since)
        resource_fields = {
            'id': fields.Integer(attribute='pk'),
            'uri': InstanceURI(resource_name),
        }

        return [marshal(row, resource_fields) for row in query.all()]


class ClientResource(Resource):
    def get(self):
        clients = [
            {
                'name': 'Shiva-Client',
                'uri': 'https://github.com/tooxie/shiva-client',
                'authors': [
                    u'Alvaro Mouriño <alvaro@mourino.net>',
                ],
            },
            {
                'name': 'Shiva4J',
                'uri': 'https://github.com/instant-solutions/shiva4j',
                'authors': [
                    u'instant:solutions <office@instant-it.at>'
                ],
            },
        ]

        return clients


class AboutResource(Resource):
    def get(self):
        info = {
            'name': 'Shiva',
            'version': get_version(),
            'author': u'Alvaro Mouriño <alvaro@mourino.net>',
            'uri': 'https://github.com/tooxie/shiva-server',
            'contributors': get_contributors(),
        }

        return info
