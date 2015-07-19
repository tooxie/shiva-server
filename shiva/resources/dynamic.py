# -*- coding: utf-8 -*-
from datetime import datetime
import urllib2
import traceback

from flask import request, current_app as app, g
from flask.ext.restful import abort, fields, marshal
import requests

from shiva.constants import HTTP
from shiva.converter import get_converter
from shiva.exceptions import InvalidMimeTypeError
from shiva.http import Resource, JSONResponse
from shiva.lyrics import get_lyrics
from shiva.mocks import ShowModel
from shiva.models import Artist, Album, Track, LyricsCache
from shiva.resources.fields import (Boolean, ForeignKeyField, InstanceURI,
                                    ManyToManyField)
from shiva.utils import get_logger

log = get_logger()


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

    limit = page_size
    offset = page_size * (page_number - 1)

    return queryset.limit(limit).offset(offset)


class LyricsResource(Resource):
    """
    The resource responsible for a track's lyrics. Lyrics are scraped on
    demand, and only the URI where they are found is stored in the database.

    """

    def get(self, id=None, slug=None):
        if not id and not slug:
            abort(HTTP.NOT_FOUND)

        if not id and slug:
            track = Track.query.filter_by(slug=slug).first()
        else:
            track = Track.query.get(id)

        return self.get_for(track)

    def get_for(self, track):
        if track.lyrics:
            return LyricsSerializer(track.lyrics).to_json()

        try:
            lyrics = get_lyrics(track)
        except:
            log.debug(traceback.format_exc())
            lyrics = None

        if not lyrics:
            abort(HTTP.NOT_FOUND)

        return LyricsSerializer(lyrics).to_json()

    def post(self, id):
        text = request.form.get('text', None)
        if not text:
            return JSONResponse(400)

        track = Track.query.get(id)
        lyric = LyricsCache(track=track, text=text)

        g.db.session.add(lyric)
        g.db.commit()

        return JSONResponse(200)

    def delete(self, id):
        track = Track.query.get(id)
        g.db.session.delete(track.lyrics)
        g.db.session.commit()

        return JSONResponse(200)


class ConvertResource(Resource):
    """ Resource in charge of converting tracks from one format to another. """

    def get(self, id):
        track = Track.query.get(id)
        mimetype = request.args.get('mimetype')
        if not track or not mimetype:
            abort(HTTP.NOT_FOUND)

        ConverterClass = get_converter()
        try:
            converter = ConverterClass(track, mimetype=mimetype)
        except InvalidMimeTypeError, e:
            log.error(e)
            abort(HTTP.NOT_FOUND)

        converter.convert()
        uri = converter.get_uri()

        return JSONResponse(status=301, headers={'Location': uri})


class ShowsResource(Resource):
    """
    """

    def get(self, id=None, slug=None):
        if not id and not slug:
            abort(HTTP.NOT_FOUND)

        if not id and slug:
            artist = Artist.query.filter_by(slug=slug).first()
        else:
            artist = Artist.query.get(id)

        if not artist:
            abort(HTTP.NOT_FOUND)

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

        log.info(bit_uri)

        try:
            response = requests.get(bit_uri)
        except requests.exceptions.RequestException:
            return

        for event in response.json():
            yield ShowsSerializer(ShowModel(artist_name, event)).to_json()


class RandomResource(Resource):
    """ Retrieves a random instance of a specified resource. """

    def get(self, resource_name):
        get_resource = getattr(self, 'get_%s' % resource_name)

        if get_resource and callable(get_resource):
            resource_fields = {
                'id': fields.Integer(attribute='pk'),
                'uri': InstanceURI(resource_name),
            }

            return marshal(get_resource(), resource_fields)

        abort(HTTP.NOT_FOUND)

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
            log.error(traceback.format_exc())
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
