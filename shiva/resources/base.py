# -*- coding: utf-8 -*-
from flask import request, current_app as app
from flask.ext.restful import abort, fields, marshal
from werkzeug.exceptions import NotFound

from shiva.http import Resource, JSONResponse
from shiva.models import Artist, Album, Track
from shiva.resources.fields import (ForeignKeyField, InstanceURI, TrackFiles,
                                    ManyToManyField)


class ArtistResource(Resource):
    """ The resource resposible for artists. """

    def get_resource_fields(self):
        return {
            'id': fields.Integer(attribute='pk'),
            'name': fields.String,
            'slug': fields.String,
            'uri': InstanceURI('artists'),
            'image': fields.String(default=app.config['DEFAULT_ARTIST_IMAGE']),
            'events_uri': fields.String(attribute='events'),
        }

    def get_by_id(self, artist_id):
        return Artist.query.get(artist_id)

    def get_by_slug(self, artist_slug):
        return Artist.query.filter_by(slug=artist_slug).first()

    def get_all(self):
        return Artist.query.order_by(Artist.name)

    def get_full_tree(self, artist):
        _artist = marshal(artist, self.get_resource_fields())
        _artist['albums'] = []

        albums = AlbumResource()

        for album in artist.albums:
            _artist['albums'].append(albums.get_full_tree(album))

        return _artist


class AlbumResource(Resource):
    """ The resource resposible for albums. """

    def get_resource_fields(self):
        return {
            'id': fields.Integer(attribute='pk'),
            'name': fields.String,
            'slug': fields.String,
            'year': fields.Integer,
            'uri': InstanceURI('albums'),
            'artists': ManyToManyField(Artist, {
                'id': fields.Integer(attribute='pk'),
                'uri': InstanceURI('artists'),
            }),
            'cover': fields.String(default=app.config['DEFAULT_ALBUM_COVER']),
        }

    def get_filters(self):
        return (
            ('artist', 'artist_filter'),
        )

    def artist_filter(self, queryset, artist_pk):
        return queryset.join(Album.artists).filter(Artist.pk == artist_pk)

    def get_by_id(self, album_id):
        return Album.query.get(album_id)

    def get_by_slug(self, album_slug):
        return Album.query.filter_by(slug=album_slug).first()

    def get_all(self):
        return Album.query.order_by(Album.year, Album.name, Album.pk)

    def get_full_tree(self, album):
        _album = marshal(album, self.get_resource_fields())
        _album['tracks'] = []

        tracks = TrackResource()

        for track in album.tracks.order_by('number', 'title'):
            _album['tracks'].append(tracks.get_full_tree(track))

        return _album


class TrackResource(Resource):
    """ The resource resposible for tracks. """

    def get_resource_fields(self):
        return {
            'id': fields.Integer(attribute='pk'),
            'uri': InstanceURI('tracks'),
            'files': TrackFiles,
            'bitrate': fields.Integer,
            'length': fields.Integer,
            'title': fields.String,
            'slug': fields.String,
            'artist': ForeignKeyField(Artist, {
                'id': fields.Integer(attribute='pk'),
                'uri': InstanceURI('artists'),
            }),
            'album': ForeignKeyField(Album, {
                'id': fields.Integer(attribute='pk'),
                'uri': InstanceURI('albums'),
            }),
            'number': fields.Integer,
        }

    def get_filters(self):
        return (
            ('artist', 'artist_filter'),
            ('album', 'album_filter'),
        )

    def artist_filter(self, queryset, artist_pk):
        return queryset.filter(Track.artist_pk == artist_pk)

    def album_filter(self, queryset, album_pk):
        return queryset.filter_by(album_pk=album_pk)

    def get_by_id(self, track_id):
        return Track.query.get(track_id)

    def get_by_slug(self, track_slug):
        return Track.query.filter_by(slug=track_slug).first()

    def get_all(self):
        return Track.query.order_by(Track.title)

    def get_full_tree(self, track, include_scraped=False,
                      include_related=True):
        """
        Retrives the full tree for a track. If the include_related option is
        not set then a normal track structure will be retrieved. If its set
        external resources that need to be scraped, like lyrics, will also be
        included. Also related objects like artist and album will be expanded
        to provide all their respective information.

        This is disabled by default to avois DoS'ing lyrics' websites when
        requesting many tracks at once.

        """

        resource_fields = self.get_resource_fields()
        if include_related:
            artist = ArtistResource()
            resource_fields['artist'] = ForeignKeyField(
                Artist,
                artist.get_resource_fields())
            album = AlbumResource()
            resource_fields['album'] = ForeignKeyField(
                Album,
                album.get_resource_fields())

        _track = marshal(track, resource_fields)

        if include_scraped:
            lyrics = LyricsResource()
            try:
                _track['lyrics'] = lyrics.get_for(track)
            except NotFound:
                _track['lyrics'] = None

        # tabs = TabsResource()
        # _track['tabs'] = tabs.get()

        return _track
