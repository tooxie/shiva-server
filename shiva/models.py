# -*- coding: utf-8 -*-
from datetime import datetime
import hashlib
import os

from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql.expression import func

from shiva.utils import slugify, MetadataManager

db = SQLAlchemy()

__all__ = ('db', 'Artist', 'Album', 'Track', 'LyricsCache')


def random_row(model):
    """Retrieves a random row for the given model."""

    try:
        # PostgreSQL, SQLite
        instance = model.query.order_by(func.random()).limit(1).first()
    except OperationalError:
        # MySQL
        instance = model.query.order_by(func.rand()).limit(1).first()

    return instance


class Artist(db.Model):
    """
    """

    __tablename__ = 'artists'

    pk = db.Column(db.Integer, primary_key=True)
    # TODO: Update the files' Metadata when changing this info.
    name = db.Column(db.String(128), nullable=False)
    slug = db.Column(db.String(128), nullable=False)
    image = db.Column(db.String(256))
    events = db.Column(db.String(256))
    date_added = db.Column(db.Date(), nullable=False)

    tracks = db.relationship('Track', backref='artist', lazy='dynamic')

    def __init__(self, *args, **kwargs):
        if 'date_added' not in kwargs:
            kwargs['date_added'] = datetime.today()

        super(Artist, self).__init__(*args, **kwargs)

    @classmethod
    def random(cls):
        return random_row(cls)

    def __setattr__(self, attr, value):
        if attr == 'name':
            super(Artist, self).__setattr__('slug', slugify(value))

        super(Artist, self).__setattr__(attr, value)

    def __repr__(self):
        return '<Artist (%s)>' % self.name


artists = db.Table('albumartists',
    db.Column('artist_pk', db.Integer, db.ForeignKey('artists.pk')),
    db.Column('album_pk', db.Integer, db.ForeignKey('albums.pk'))
)


class Album(db.Model):
    """
    """

    __tablename__ = 'albums'

    pk = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    slug = db.Column(db.String(128), nullable=False)
    year = db.Column(db.Integer)
    cover = db.Column(db.String(256))
    date_added = db.Column(db.Date(), nullable=False)

    tracks = db.relationship('Track', backref='album', lazy='dynamic')

    artists = db.relationship('Artist', secondary=artists,
                              backref=db.backref('albums', lazy='dynamic'))

    def __init__(self, *args, **kwargs):
        if 'date_added' not in kwargs:
            kwargs['date_added'] = datetime.today()

        super(Album, self).__init__(*args, **kwargs)

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
    """Track model."""

    __tablename__ = 'tracks'

    pk = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.Unicode(256), unique=True, nullable=False)
    title = db.Column(db.String(128))
    slug = db.Column(db.String(128))
    bitrate = db.Column(db.Integer)
    file_size = db.Column(db.Integer)
    # TODO could be float if number weren't converted to an int in metadata
    # manager
    length = db.Column(db.Integer)
    # TODO number should probably be renamed to track or track_number
    number = db.Column(db.Integer)
    date_added = db.Column(db.Date(), nullable=False)
    hash = db.Column(db.String(32))

    lyrics = db.relationship('LyricsCache', backref='track', uselist=False)

    album_pk = db.Column(db.Integer, db.ForeignKey('albums.pk'), nullable=True)
    artist_pk = db.Column(db.Integer, db.ForeignKey('artists.pk'),
                          nullable=True)

    def __init__(self, path, *args, **kwargs):
        if not isinstance(path, (basestring, file)):
            raise ValueError('Invalid parameter for Track. Path or File '
                             'expected, got %s' % type(path))

        _path = path
        if isinstance(path, file):
            _path = path.name

        no_metadata = False
        if 'no_metadata' in kwargs:
            no_metadata = kwargs.get('no_metadata', False)
            del(kwargs['no_metadata'])

        hash_file = False
        if 'hash_file' in kwargs:
            hash_file = kwargs.get('hash_file', False)
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
            super(Track, self).__setattr__('slug', slugify(value))

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
                self.number = meta.track_number
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


class LyricsCache(db.Model):
    """
    """

    __tablename__ = 'lyricscache'

    pk = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    source = db.Column(db.String(256))

    track_pk = db.Column(db.Integer, db.ForeignKey('tracks.pk'),
                         nullable=False)

    def __repr__(self):
        return "<LyricsCache ('%s')>" % self.track.title
