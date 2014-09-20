# -*- coding: utf-8 -*-
from flask import current_app as app, request, url_for
from flask.ext.restful import abort, fields, marshal
from werkzeug.exceptions import NotFound

from shiva.exceptions import (InvalidFileTypeError, IntegrityError,
                              ObjectExistsError)
from shiva.http import Resource
from shiva.models import Album, Artist, db, Track, User
from shiva.resources.fields import (ForeignKeyField, InstanceURI, TrackFiles,
                                    ManyToManyField)
from shiva.utils import parse_bool


class ArtistResource(Resource):
    """ The resource responsible for artists. """

    def __init__(self, *args, **kwargs):
        self.db_model = Artist

        super(ArtistResource, self).__init__(*args, **kwargs)

    def get_resource_fields(self):
        return {
            'id': fields.Integer(attribute='pk'),
            'name': fields.String,
            'slug': fields.String,
            'uri': InstanceURI('artists'),
            'image': fields.String(default=app.config['DEFAULT_ARTIST_IMAGE']),
            'events_uri': fields.String(attribute='events'),
        }

    def post(self):
        name = request.values.get('name')
        image_url = request.values.get('image_url')

        try:
            artist = self.create(name, image_url)
        except (IntegrityError, ObjectExistsError):
            abort(409)

        response = marshal(artist, self.get_resource_fields())
        headers = {'Location': url_for('artists', id=artist.pk)}

        return response, 201, headers

    def create(self, name, image_url):
        artist = Artist(name=name, image=image_url)

        db.session.add(artist)
        db.session.commit()

        return artist

    def update(self, artist):
        artist.name = request.form.get('name')
        artist.image = request.form.get('image')

        db.session.add(artist)
        db.session.commit()

    def get_full_tree(self, artist):
        _artist = marshal(artist, self.get_resource_fields())
        _artist['albums'] = []

        albums = AlbumResource()

        for album in artist.albums:
            _artist['albums'].append(albums.get_full_tree(album))

        no_album = artist.tracks.filter(Track.albums == None).all()
        track_fields = TrackResource().get_resource_fields()
        _artist['no_album_tracks'] = marshal(no_album, track_fields)

        return _artist


class AlbumResource(Resource):
    """ The resource responsible for albums. """

    def __init__(self, *args, **kwargs):
        self.db_model = Album

        super(AlbumResource, self).__init__(*args, **kwargs)

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

    def post(self):
        params = {
            'name': request.values.get('name'),
            'year': request.values.get('year'),
            'cover_url': request.values.get('cover_url'),
            'artists': request.values.getlist('artist_id'),
        }

        try:
            album = self.create(**params)
        except (IntegrityError, ObjectExistsError):
            abort(409)

        response = marshal(album, self.get_resource_fields())
        headers = {'Location': url_for('albums', id=album.pk)}

        return response, 201, headers

    # TODO: Document creation of objects and multivalued arguments
    # (i.e. /albums?name=Derp&artist_id=1&artist_id2)
    def create(self, name, year, cover_url, artists=[]):
        albums = Album.query.filter_by(name=name).all()
        for album in albums:
            if album.artists == artists:
                raise ObjectExistsError

            if map(lambda a: a.pk in artists, album.artists):
                raise ObjectExistsError

        album = Album(name=name, year=year, cover=cover_url)

        for artist in artists:
            album.artists.append(Artist.query.get(artist))

        db.session.add(album)
        db.session.commit()

        return album

    def update(self, album):
        """
        Updates an album object with the given attributes. The `artists`
        attribute, however, is treated as a calculated value so it cannot be
        set through a PUT request. It has to be done through the Track model.
        """

        album.name = request.form.get('name')
        album.year = request.form.get('year')
        album.cover = request.form.get('cover_url')

        db.session.add(album)
        db.session.commit()

    def get_filters(self):
        return (
            ('artist', 'artist_filter'),
        )

    def artist_filter(self, queryset, artist_pk):
        try:
            pk = artist_pk if int(artist_pk) > 0 else None
        except ValueError:
            abort(400)

        return queryset.join(Album.artists).filter(Artist.pk == pk)

    def get_full_tree(self, album):
        _album = marshal(album, self.get_resource_fields())
        _album['tracks'] = []

        tracks = TrackResource()

        for track in album.tracks.order_by(Track.ordinal, Track.title):
            _album['tracks'].append(tracks.get_full_tree(track))

        return _album


class TrackResource(Resource):
    """ The resource responsible for tracks. """

    def __init__(self, *args, **kwargs):
        self.db_model = Track

        super(TrackResource, self).__init__(*args, **kwargs)

    def get_resource_fields(self):
        return {
            'id': fields.Integer(attribute='pk'),
            'uri': InstanceURI('tracks'),
            'files': TrackFiles,
            'bitrate': fields.Integer,
            'length': fields.Integer,
            'title': fields.String,
            'slug': fields.String,
            'artists': ManyToManyField(Artist, {
                'id': fields.Integer(attribute='pk'),
                'uri': InstanceURI('artists'),
            }),
            'albums': ManyToManyField(Album, {
                'id': fields.Integer(attribute='pk'),
                'uri': InstanceURI('albums'),
            }),
            'ordinal': fields.Integer,
        }

    def post(self):
        params = {
            'title': request.values.get('title'),
            'artist_id': request.values.get('artist_id'),
            'album_id': request.values.get('album_id'),
            'ordinal': request.values.get('ordinal'),
        }

        try:
            track = self.create(**params)
        except (IntegrityError, ObjectExistsError):
            abort(409)

        response = marshal(track, self.get_resource_fields())
        headers = {'Location': url_for('tracks', id=track.pk)}

        return response, 201, headers

    def create(self, title, artist_id, album_id, ordinal):
        if not request.files:
            abort(400)

        UploadHandler = app.config.get('UPLOAD_HANDLER')
        try:
            handler = UploadHandler(track=request.files.get('track'))
        except InvalidFileTypeError, e:
            abort(415)  # Unsupported Media Type

        handler.save()

        # TODO: Document this.
        hash_file = parse_bool(request.form.get('hash_file', True))
        no_metadata = parse_bool(request.form.get('no_metadata', False))

        track = Track(path=handler.path, hash_file=hash_file,
                      no_metadata=no_metadata)
        db.session.add(track)

        if handler.artist:
            artist = Artist.query.filter_by(name=handler.artist).first()
            if not artist:
                artist = Artist(name=handler.artist)
                db.session.add(artist)

            artist.tracks.append(track)

        if handler.album:
            album = Album.query.filter_by(name=handler.album).first()
            if not album:
                album = Album(name=handler.album)
                db.session.add(album)

            album.tracks.append(track)

        db.session.commit()

        return track

    def update(self, track):
        track.title = request.form.get('title')
        track.ordinal = request.form.get('ordinal')

        for artist_pk in request.form.getlist('artist_id'):
            try:
                artist = Artist.query.get(artist_pk)
                track.artists.append(artist)
            except:
                pass

        for album_pk in request.form.getlist('album_id'):
            try:
                album = Album.query.get(album_pk)
                track.albums.append(album)
            except:
                pass

        db.session.add(track)
        db.session.commit()

    def get_filters(self):
        return (
            ('artist', 'artist_filter'),
            ('album', 'album_filter'),
        )

    def artist_filter(self, queryset, artist_pk):
        try:
            pk = artist_pk if int(artist_pk) > 0 else None
        except ValueError:
            abort(400)

        return queryset.filter(Track.artist_pk == pk)

    def album_filter(self, queryset, album_pk):
        try:
            pk = album_pk if int(album_pk) > 0 else None
        except ValueError:
            abort(400)

        return queryset.filter_by(album_pk=pk)

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


class UserResource(Resource):
    """ The resource responsible for users. """

    def get_resource_fields(self):
        return {
            'id': fields.Integer(attribute='pk'),
            'email': fields.String,
        }

    def post(self):
        email = request.values.get('email')
        if not email:
            abort(400)

        password = request.values.get('password')

        try:
            user = self.create(email=email, password=password)
        except (IntegrityError, ObjectExistsError):
            abort(409)

        response = marshal(user, self.get_resource_fields())
        headers = {'Location': url_for('users', id=user.pk)}

        return response, 201, headers

    def create(self, email, password):
        user = User(email=email, password=password)

        db.session.add(user)
        db.session.commit()

        return user

    # TODO: PUT


class ClientResource(Resource):
    pass
