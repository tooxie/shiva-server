# -*- coding: utf-8 -*-
from flask import current_app as app, g, request, url_for
from flask.ext.restful import abort
from werkzeug.exceptions import NotFound

from shiva.auth import Roles
from shiva.constants import HTTP
from shiva.exceptions import (InvalidFileTypeError, IntegrityError,
                              ObjectExistsError)
from shiva.http import Resource
from shiva.lyrics import get_lyrics
from shiva.models import Album, Artist, db, Track, User, Playlist
from shiva.resources import serializers
from shiva.utils import parse_bool, get_list, get_by_name


class ArtistResource(Resource):
    """ The resource responsible for artists. """

    db_model = Artist
    serializer = serializers.ArtistSerializer

    def post(self):
        name = request.form.get('name', '').strip()
        if not name:
            abort(HTTP.BAD_REQUEST)

        image_url = request.form.get('image_url')

        try:
            artist = self.create(name, image_url)
        except (IntegrityError, ObjectExistsError):
            abort(HTTP.CONFLICT)

        response = self.serializer(artist).to_json()
        headers = {'Location': url_for('artists', id=artist.pk)}

        return response, 201, headers

    def create(self, name, image_url):
        artist = Artist(name=name, image=image_url)

        db.session.add(artist)
        db.session.commit()

        return artist

    def update(self, artist):
        if 'name' in request.form:
            name = request.form.get('name', '').strip()
            if not name:
                abort(HTTP.BAD_REQUEST)

            artist.name = name

        if 'image' in request.form:
            artist.image = request.form.get('image_url')

        return artist

    def get_full_tree(self, artist):
        serializer = self.serializer(artist)
        serializer.add_raw_field({
            'albums': AlbumResource.serializer(artist.albums).to_json()
        })

        no_album_tracks = artist.tracks.filter_by(albums=None).all()
        track_serializer = serializers.TrackSerializer(no_album_tracks)
        serializer.add_raw_field({
            'no_album_tracks': track_serializer.to_json()
        })

        return serializer.to_json(recursive=True)


class AlbumResource(Resource):
    """ The resource responsible for albums. """

    db_model = Album
    serializer = serializers.AlbumSerializer

    def post(self):
        params = {
            'name': request.form.get('name', '').strip(),
            'year': request.form.get('year'),
            'cover_url': request.form.get('cover_url'),
        }

        if not params['name']:
            abort(HTTP.BAD_REQUEST)

        album = self.create(**params)

        response = self.serializer(album).to_json()
        headers = {'Location': url_for('albums', id=album.pk)}

        return response, 201, headers

    def create(self, name, year, cover_url):
        album = Album(name=name, year=year, cover=cover_url)

        db.session.add(album)
        db.session.commit()

        return album

    def update(self, album):
        """
        Updates an album object with the given attributes. The `artists`
        attribute, however, is treated as a calculated value so it cannot be
        set through a PUT request. It has to be done through the Track model.
        """

        if 'name' in request.form:
            name = request.form.get('name', '').strip()
            if not name:
                abort(HTTP.BAD_REQUEST)

            album.name = request.form.get('name')

        if 'year' in request.form:
            album.year = request.form.get('year')

        if 'cover_url' in request.form:
            album.cover = request.form.get('cover_url')

        return album

    def get_filters(self):
        return (
            ('artist', 'artist_filter'),
        )

    def artist_filter(self, queryset, artist_pk):
        try:
            pk = artist_pk if int(artist_pk) > 0 else None
        except ValueError:
            abort(HTTP.BAD_REQUEST)

        return queryset.join(Album.artists).filter(Artist.pk == pk)

    def get_full_tree(self, album):
        serializer = self.serializer(album)
        _tracks = album.tracks.order_by(Track.ordinal, Track.title).all()
        serializer.add_raw_field({
            'tracks': TrackResource.serializer(_tracks).to_json()
        })

        return serializer.to_json()


class TrackResource(Resource):
    """ The resource responsible for tracks. """

    db_model = Track
    serializer = serializers.TrackSerializer

    def post(self):
        params = {
            'title': request.form.get('title', '').strip(),
            'artists': request.form.getlist('artist_id'),
            'albums': request.form.getlist('album_id'),
            'ordinal': request.form.get('ordinal'),
        }

        if 'track' not in request.files:
            abort(HTTP.BAD_REQUEST)

        try:
            track = self.create(**params)
        except (IntegrityError, ObjectExistsError):
            abort(HTTP.CONFLICT)

        response = self.serializer(track).to_json()
        headers = {'Location': url_for('tracks', id=track.pk)}

        return response, 201, headers

    def create(self, title, artists, albums, ordinal):
        UploadHandler = app.config.get('UPLOAD_HANDLER')
        try:
            handler = UploadHandler(track=request.files.get('track'))
        except InvalidFileTypeError, e:
            abort(HTTP.UNSUPPORTED_MEDIA_TYPE)

        handler.save()

        hash_file = parse_bool(request.args.get('hash_file', True))
        no_metadata = parse_bool(request.args.get('no_metadata', False))

        track = Track(path=handler.path, hash_file=hash_file,
                      no_metadata=no_metadata)
        db.session.add(track)

        # If an artist (or album) is given as argument, it will take precedence
        # over whatever the file's metadata say.
        artist_list = []
        if artists:
            try:
                artist_list.extend(get_list(Artist, artists))
            except ValueError:
                abort(HTTP.BAD_REQUEST)
        else:
            if handler.artist:
                artist_list.append(get_by_name(Artist, handler.artist))

        album_list = []
        if albums:
            try:
                album_list.extend(get_list(Album, albums))
            except ValueError:
                abort(HTTP.BAD_REQUEST)
        else:
            if handler.album:
                artist_list.append(get_by_name(Album, handler.album))

        for artist in artist_list:
            db.session.add(artist)
            artist.tracks.append(track)

        for album in album_list:
            db.session.add(album)
            album.tracks.append(track)

        db.session.commit()

        return track

    def update(self, track):
        track.title = request.form.get('title')
        track.ordinal = request.form.get('ordinal')

        # The track attribute cannot be updated. A new track has to be created
        # with the new value instead.
        if 'track' in request.form:
            abort(HTTP.BAD_REQUEST)

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

        return track

    def get_filters(self):
        return (
            ('artist', 'artist_filter'),
            ('album', 'album_filter'),
        )

    def artist_filter(self, queryset, artist_pk):
        try:
            pk = artist_pk if int(artist_pk) > 0 else None
        except ValueError:
            abort(HTTP.BAD_REQUEST)

        return queryset.filter(Track.artist_pk == pk)

    def album_filter(self, queryset, album_pk):
        try:
            pk = album_pk if int(album_pk) > 0 else None
        except ValueError:
            abort(HTTP.BAD_REQUEST)

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

        serializer = self.serializer(track)

        if include_related:
            serializer.add_m2m_rel(key='artists', db_model=Artist,
                                   serializer=serializers.ArtistSerializer)
            serializer.add_m2m_rel(key='albums', db_model=Album,
                                   serializer=serializers.AlbumSerializer)
        if include_scraped:
            serializer.update_schema({'lyrics': get_lyrics(track)})
            # serializer.update_schema({'tabs': get_tabs(track)})

        return serializer.to_json()


class PlaylistResource(Resource):
    """
    Playlist are just a logical collection of tracks. Tracks must not be
    necessarily related between them in any way.

    To access a user's playlists filter by user id:

        /playlists?user_id=6

    """

    db_model = Playlist
    serializer = serializers.PlaylistSerializer

    def post(self):
        if g.user is None:
            abort(HTTP.BAD_REQUEST)

        name = request.form.get('name', '').strip()
        if not name:
            abort(HTTP.BAD_REQUEST)

        read_only = request.form.get('read_only', True)

        playlist = self.create(name=name, read_only=read_only, user=g.user)

        response = self.serializer(playlist).to_json()
        headers = {'Location': url_for('playlists', id=playlist.pk)}

        return response, 201, headers

    def create(self, name, read_only, user):
        playlist = Playlist(name=name, read_only=read_only, user=user)

        db.session.add(playlist)
        db.session.commit()

        return playlist

    def update(self, playlist):
        if 'name' in request.form:
            playlist.name = request.form.get('name')

        if 'read_only' in request.form:
            playlists.read_only = parse_bool(request.form.get('read_only'))

        return playlist


class PlaylistTrackResource(Resource):
    """
    While PlaylistResource is used to create and update playlists and their
    attributes, PlaylistTrackResource is used to manipulate the tracks
    contained in the playlist.

    """

    def post(self, id, verb):
        handler = getattr(self, '%s_track' % verb)
        if not handler:
            abort(HTTP.BAD_REQUEST)

        playlist = self.get_playlist(id)
        if not playlist:
            abort(HTTP.NOT_FOUND)

        return handler(playlist)

    def add_track(self, playlist):
        if 'track' not in request.form:
            abort(HTTP.BAD_REQUEST)

        track = self.get_track(request.form.get('track'))
        if not track:
            abort(HTTP.BAD_REQUEST)

        try:
            playlist.insert(request.form.get('index'), track)
        except ValueError:
            abort(HTTP.BAD_REQUEST)

        return self.Response('')

    def remove_track(self, playlist):
        if 'index' not in request.form:
            abort(HTTP.BAD_REQUEST)

        try:
            playlist.remove_at(request.form.get('index'))
        except (ValueError, IndexError):
            abort(HTTP.BAD_REQUEST)

        return self.Response('')

    def get_playlist(self, playlist_id):
        try:
            playlist = Playlist.query.get(playlist_id)
        except:
            playlist = None

        return playlist

    def get_track(self, track_id):
        try:
            track = Track.query.get(track_id)
        except:
            track = None

        return track


class UserResource(Resource):
    """ The resource responsible for users. """

    db_model = User
    serializer = serializers.UserSerializer

    def get(self, id=None):
        if id == 'me':
            return serializers.UserSerializer(g.user).to_json()

        return super(UserResource, self).get(id)

    def get_all(self):
        return self.db_model.query.filter_by(is_public=True)

    def post(self, id=None):
        if id == 'me':
            abort(HTTP.METHOD_NOT_ALLOWED)

        if g.user is None:
            abort(HTTP.METHOD_NOT_ALLOWED)

        email = request.form.get('email')
        if not email:
            abort(HTTP.BAD_REQUEST)

        display_name = request.form.get('display_name')
        is_active = False
        password = request.form.get('password')
        if password:
            is_active = parse_bool(request.form.get('is_active', False))
        # FIXME: Check permissions
        is_admin = parse_bool(request.form.get('admin', False))

        try:
            user = self.create(display_name=display_name, email=email,
                               password=password, is_active=is_active,
                               is_admin=is_admin)
        except (IntegrityError, ObjectExistsError):
            abort(HTTP.CONFLICT)

        response = serializers.UserSerializer(user).to_json()
        headers = {'Location': url_for('users', id=user.pk)}

        return response, 201, headers

    def create(self, display_name, email, password, is_active, is_admin):
        role = Roles.get('ADMIN' if is_admin else 'USER')
        user = User(display_name=display_name, email=email, password=password,
                    is_active=is_active, role=role)

        db.session.add(user)
        db.session.commit()

        return user

    def put(self, id=None):
        if id == 'me':
            abort(HTTP.METHOD_NOT_ALLOWED)

        return super(UserResource, self).put(id)

    def update(self, user):
        if 'email' in request.form:
            email = request.form.get('email', '').strip()
            if not email:
                abort(HTTP.BAD_REQUEST)

            user.email = email

        if 'display_name' in request.form:
            user.display_name = request.form.get('display_name')

        if 'password' in request.form:
            user.password = request.form.get('password')

        if user.password == '':
            user.is_active = False
        else:
            if 'is_active' in request.form:
                user.is_active = parse_bool(request.form.get('is_active'))

        if 'is_admin' in request.form:
            is_admin = parse_bool(request.form.get('is_admin'))
            user.role = Roles.get('ADMIN' if is_admin else 'USER')

        return user

    def delete(self, id=None):
        if id == 'me':
            abort(HTTP.METHOD_NOT_ALLOWED)

        return super(UserResource, self).delete(id)
