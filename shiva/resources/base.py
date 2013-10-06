# -*- coding: utf-8 -*-
from flask import request, current_app as app, g
from flask.ext.restful import abort, fields, marshal
from werkzeug.exceptions import NotFound

from shiva.http import Resource, JSONResponse
from shiva.models import Artist, Album, Track
from shiva.resources.fields import (ForeignKeyField, InstanceURI, TrackFiles,
                                    ManyToManyField)


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

    limit = page_size
    offset = page_size * (page_number - 1)

    return queryset.limit(limit).offset(offset)


class ArtistResource(Resource):
    """ The resource resposible for artists. """

    def get_resource_fields(self):
        return {
            'id': fields.Integer(attribute='pk'),
            'name': fields.String,
            'slug': fields.String,
            'uri': InstanceURI('artist'),
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
    """ The resource resposible for albums. """

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

        tracks = TrackResource()

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


class TrackResource(Resource):
    """ The resource resposible for tracks. """

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
            return self.get_full_tree(track, include_scraped=True,
                                      include_related=True)

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
            if full_tree():
                yield self.get_full_tree(track, include_related=True)
            else:
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

    def get_full_tree(self, track, include_scraped=False,
                      include_related=False):
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

    def delete(self, track_id=None):
        if not track_id:
            return JSONResponse(405)

        track = Track.query.get(track_id)
        if not track:
            abort(404)

        g.db.session.delete(track)
        g.db.session.commit()

        return {}
