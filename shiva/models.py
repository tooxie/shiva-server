# -*- coding: utf-8 -*-
from datetime import datetime
import bcrypt
import hashlib
import os
import uuid

from flask import current_app as app
from flask.ext.sqlalchemy import SQLAlchemy
from itsdangerous import (BadSignature, SignatureExpired,
                          TimedJSONWebSignatureSerializer as Serializer)
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql.expression import func
from slugify import slugify

from shiva import dbtypes
from shiva.auth import Roles
from shiva.utils import MetadataManager

db = SQLAlchemy()

__all__ = ('db', 'Artist', 'Album', 'Track', 'LyricsCache', 'User')


def random_row(model):
    """Retrieves a random row for the given model."""

    try:
        # PostgreSQL, SQLite
        instance = model.query.order_by(func.random()).limit(1).first()
    except OperationalError:
        # MySQL
        instance = model.query.order_by(func.rand()).limit(1).first()

    return instance


# Table relationships
track_artist = db.Table('trackartist',
    db.Column('track_pk', dbtypes.GUID, db.ForeignKey('tracks.pk')),
    db.Column('artist_pk', dbtypes.GUID, db.ForeignKey('artists.pk')),
)

track_album = db.Table('trackalbum',
    db.Column('track_pk', dbtypes.GUID, db.ForeignKey('tracks.pk')),
    db.Column('album_pk', dbtypes.GUID, db.ForeignKey('albums.pk')),
)


class Artist(db.Model):
    __tablename__ = 'artists'

    pk = db.Column(dbtypes.GUID, default=uuid.uuid4, primary_key=True)
    # TODO: Update the files' Metadata when changing this info.
    name = db.Column(db.String(128), unique=True, nullable=False)
    slug = db.Column(db.String(128))
    image = db.Column(db.String(256))
    events = db.Column(db.String(256))
    date_added = db.Column(db.Date(), nullable=False)

    def __init__(self, *args, **kwargs):
        if 'date_added' not in kwargs:
            kwargs['date_added'] = datetime.today()

        super(Artist, self).__init__(*args, **kwargs)

    @property
    def albums(self):
        # FIXME: Optimize. Check comments for Album.artists method.
        albums = []

        for track in self.tracks:
            for album in track.albums:
                if album not in albums:
                    albums.append(album)

        return albums

    @classmethod
    def random(cls):
        return random_row(cls)

    def __setattr__(self, attr, value):
        if attr == 'name':
            super(Artist, self).__setattr__('slug', slugify(value))

        super(Artist, self).__setattr__(attr, value)

    def __repr__(self):
        return '<Artist (%s)>' % self.name


class Album(db.Model):
    __tablename__ = 'albums'

    pk = db.Column(dbtypes.GUID, default=uuid.uuid4, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    slug = db.Column(db.String(128))
    year = db.Column(db.Integer)
    cover = db.Column(db.String(256))
    date_added = db.Column(db.Date(), nullable=False)

    def __init__(self, *args, **kwargs):
        if 'date_added' not in kwargs:
            kwargs['date_added'] = datetime.today()

        super(Album, self).__init__(*args, **kwargs)

    @property
    def artists(self):
        """
        Calculates the artists for this album by traversing the list of tracks.
        This is a terrible way of doing this, but we assume that the worst case
        will still be good enough to defer the optimization of this method for
        the future.
        """

        artists = []

        # FIXME: Optimize
        for track in self.tracks:
            for artist in track.artists:
                if artist not in artists:
                    artists.append(artist)

        return artists

    @classmethod
    def random(cls):
        return random_row(cls)

    def __setattr__(self, attr, value):
        if attr == 'name':
            super(Album, self).__setattr__('slug', slugify(value))

        super(Album, self).__setattr__(attr, value)

    def __repr__(self):
        return '<Album (%s)>' % self.name


class Track(db.Model):
    __tablename__ = 'tracks'

    pk = db.Column(dbtypes.GUID, default=uuid.uuid4, primary_key=True)
    path = db.Column(db.Unicode(256), unique=True, nullable=False)
    title = db.Column(db.String(128))
    slug = db.Column(db.String(128))
    bitrate = db.Column(db.Integer)
    file_size = db.Column(db.Integer)
    length = db.Column(db.Integer)
    ordinal = db.Column(db.Integer)
    date_added = db.Column(db.Date(), nullable=False)
    hash = db.Column(db.String(32))

    lyrics = db.relationship('LyricsCache', backref='tracks', uselist=False)
    albums = db.relationship('Album', secondary=track_album, lazy='dynamic',
                             backref=db.backref('tracks', lazy='dynamic'))
    artists = db.relationship('Artist', secondary=track_artist, lazy='dynamic',
                              backref=db.backref('tracks', lazy='dynamic'))

    def __init__(self, path, *args, **kwargs):
        if not isinstance(path, (basestring, file)):
            raise ValueError('Invalid parameter for Track. Path or File '
                             'expected, got %s' % type(path))

        _path = path
        if isinstance(path, file):
            _path = path.name

        no_metadata = kwargs.get('no_metadata', False)
        if 'no_metadata' in kwargs:
            del(kwargs['no_metadata'])

        hash_file = kwargs.get('hash_file', False)
        if 'hash_file' in kwargs:
            del(kwargs['hash_file'])

        self._meta = None
        self.set_path(_path, no_metadata=no_metadata)
        if hash_file:
            self.hash = self.calculate_hash()

        if 'date_added' not in kwargs:
            kwargs['date_added'] = datetime.today()

        super(Track, self).__init__(*args, **kwargs)

    @classmethod
    def random(cls):
        return random_row(cls)

    def __setattr__(self, attr, value):
        if attr == 'title':
            slug = slugify(value) if value else None
            super(Track, self).__setattr__('slug', slug)

        super(Track, self).__setattr__(attr, value)

    def get_path(self):
        if self.path:
            return self.path.encode('utf-8')

        return None

    def set_path(self, path, no_metadata=False):
        if path != self.get_path():
            self.path = path
            if no_metadata:
                return None

            if os.path.exists(self.get_path()):
                meta = self.get_metadata_reader()
                self.file_size = meta.filesize
                self.bitrate = meta.bitrate
                self.length = meta.length
                self.ordinal = meta.track_number
                self.title = meta.title

    def calculate_hash(self):
        md5 = hashlib.md5()
        block_size = 128 * md5.block_size

        with open(self.get_path(), 'rb') as f:
            for chunk in iter(lambda: f.read(block_size), b''):
                md5.update(chunk)

        return md5.hexdigest()

    def get_metadata_reader(self):
        """Return a MetadataManager object."""
        if not getattr(self, '_meta', None):
            self._meta = MetadataManager(self.get_path())

        return self._meta

    def __repr__(self):
        return "<Track ('%s')>" % self.title


class TrackPlaylistRelationship(db.Model):
    __tablename__ = 'trackplaylist'

    pk = db.Column(dbtypes.GUID, default=uuid.uuid4, primary_key=True)
    track_pk = db.Column(dbtypes.GUID, db.ForeignKey('tracks.pk'),
                         nullable=False)
    playlist_pk = db.Column(dbtypes.GUID, db.ForeignKey('playlists.pk'),
                            nullable=False)
    previous_track_pk = db.Column(dbtypes.GUID,
                                  db.ForeignKey('trackplaylist.pk'))

    track = db.relationship('Track')
    playlist = db.relationship('Playlist')
    previous_track = db.relationship('TrackPlaylistRelationship',
                                     uselist=False)

    def __repr__(self):
        return "<TrackPlaylistRelationship ('%s')>" % (self.pk)


class Playlist(db.Model):
    __tablename__ = 'playlists'

    pk = db.Column(dbtypes.GUID, default=uuid.uuid4, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    read_only = db.Column(db.Boolean, nullable=False, default=True)
    user_pk = db.Column(dbtypes.GUID, db.ForeignKey('users.pk'),
                        nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User')
    tracks = db.relationship('Track', backref='playlists', lazy='dynamic',
        secondary='trackplaylist',
        primaryjoin=(pk == TrackPlaylistRelationship.playlist_pk))

    def __init__(self, *args, **kwargs):
        kwargs['creation_date'] = datetime.now()

        super(Playlist, self).__init__(*args, **kwargs)

    def remove_at(self, index=None):
        """
        Removes an item from the playlist. The playlist is a linked list, so
        this method takes care of removing the element and updating any links
        to it.
        """

        try:
            index = int(index)
        except:
            raise ValueError

        if index < 0:
            raise ValueError

        query = TrackPlaylistRelationship.query.filter_by(playlist=self)
        count = query.count()
        if index >= count:
            raise IndexError

        # Playlist-track relationship
        r_track = self.get_track_at(index)
        next_track = TrackPlaylistRelationship.query.filter(
            TrackPlaylistRelationship.playlist == self,
            TrackPlaylistRelationship.previous_track == r_track).first()

        if next_track:
            # Update linked list
            next_track.previous_track = r_track.previous_track
            db.session.add(next_track)

        # import ipdb; ipdb.set_trace()
        db.session.delete(r_track)
        db.session.commit()

    def insert(self, index, track):
        """
        Inserts a track in the playlist. The playlist tracks are structured in
        a linked list, to insert an item in the list this method find the item
        in the right position and updates the links in both.

        If the value None is given as index, the track will be appended at the
        end of the list.
        """

        if index is not None:
            try:
                index = int(index)
            except:
                raise ValueError

            if index < 0:
                raise ValueError

        if track is None:
            raise ValueError

        rel = TrackPlaylistRelationship(playlist=self, track=track)

        query = TrackPlaylistRelationship.query.filter_by(playlist=self)
        count = query.count()

        if index is None:
            index = count

        if count == 0 and index > 0:
            raise ValueError

        if count > 0:
            if index > count:
                raise ValueError

            # r_track is not an actual track, but a relationship between the
            # playlist and a track.
            if index == count:  # Append at the end
                r_track = self.get_track_at(index - 1)
                rel.previous_track = r_track
            else:
                r_track = self.get_track_at(index)
                if not r_track:
                    raise ValueError
                rel.previous_track = r_track.previous_track
                r_track.previous_track = rel

            db.session.add(r_track)

        db.session.add(rel)
        db.session.commit()

    def get_track_at(self, index):
        """
        This method finds the track at position `index` in the current
        playlist. Will return None if the track is not present.

        It fetches the playlist's parent (the track with `previous_track_pk`
        None) and queries for each susequent item until the requested item is
        found.  This implementation is the slowest, but for now is ok because
        is also the simplest.

        This is a very good candidate for optimization.
        """

        counter = 0
        # Get the parent
        track = TrackPlaylistRelationship.query.filter_by(
            playlist=self, previous_track=None).first()

        while True:
            if counter == index:
                return track
            elif counter > index:
                return None

            track = TrackPlaylistRelationship.query.filter(
                TrackPlaylistRelationship.playlist == self,
                TrackPlaylistRelationship.previous_track == track).first()
            counter += 1

    @property
    def length(self):
        query = TrackPlaylistRelationship.query.filter_by(playlist=self)

        return query.count()

    def __repr__(self):
        return "<Playlist ('%s')" % self.name


class LyricsCache(db.Model):
    __tablename__ = 'lyricscache'

    pk = db.Column(dbtypes.GUID, default=uuid.uuid4, primary_key=True)
    text = db.Column(db.Text)
    source = db.Column(db.String(256))

    track_pk = db.Column(dbtypes.GUID, db.ForeignKey('tracks.pk'),
                         nullable=False)

    def __repr__(self):
        return "<LyricsCache ('%s')>" % self.track.title


class User(db.Model):
    __tablename__ = 'users'

    pk = db.Column(dbtypes.GUID, default=uuid.uuid4, primary_key=True)
    display_name = db.Column(db.String(256))
    email = db.Column(db.String(256), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=True)
    salt = db.Column(db.String(256), nullable=True)

    # Metadata
    # Should these attributes be in their own table?
    is_public = db.Column(db.Boolean, nullable=False, default=False)
    is_active = db.Column(db.Boolean, nullable=False, default=False)
    role = db.Column(db.Enum(*Roles.as_tuple()), nullable=False,
                     default=Roles.USER)
    creation_date = db.Column(db.DateTime, nullable=False)

    def __init__(self, *args, **kwargs):
        kwargs['creation_date'] = datetime.now()

        super(User, self).__init__(*args, **kwargs)

    def __setattr__(self, *args, **kwargs):
        if args[0] == 'password':
            password = args[1]
            salt = None

            if password not in (None, ''):
                password, salt = self.hash_password(password)

            self.salt = salt
            args = ('password', password)

        super(User, self).__setattr__(*args, **kwargs)

    def hash_password(self, password, salt=None):
        salt = salt or self.salt or bcrypt.gensalt()
        _pass = bcrypt.hashpw(password.encode('utf-8'), salt.encode('utf-8'))

        return (_pass, salt)

    def verify_password(self, password):
        _password, salt = self.hash_password(password)

        return _password == self.password

    def generate_auth_token(self, expiration=None):
        if not expiration:
            expiration = app.config.get('AUTH_EXPIRATION_TIME', 3600)

        if not isinstance(expiration, int):
            raise ValueError

        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)

        return s.dumps({'pk': str(self.pk)})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])

        try:
            data = s.loads(token)
        except (SignatureExpired, BadSignature):
            return None

        user = User.query.get(data['pk'])

        return user

    def __repr__(self):
        return "<User ('%s')>" % self.email
