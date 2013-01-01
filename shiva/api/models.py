# -*- coding: utf-8 -*-
import os

from flask.ext.sqlalchemy import SQLAlchemy

from shiva.utils import slugify, ID3Manager

db = SQLAlchemy()

__all__ = ('db', 'Artist', 'Album', 'Track')


class Artist(db.Model):
    """
    """

    __tablename__ = 'artists'

    pk = db.Column(db.Integer, primary_key=True)
    # TODO: Update the files' ID3 tags when changing this info.
    name = db.Column(db.String(128), nullable=False)
    image = db.Column(db.String(256))
    slug = db.Column(db.String(), nullable=False)

    tracks = db.relationship('Track', backref='artist', lazy='dynamic')

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
    name = db.Column(db.String(128), unique=True)
    year = db.Column(db.Integer)
    cover = db.Column(db.String(256))
    slug = db.Column(db.String(), nullable=False)

    tracks = db.relationship('Track', backref='album', lazy='dynamic')

    artists = db.relationship('Artist', secondary=artists,
                              backref=db.backref('albums', lazy='dynamic'))

    def __setattr__(self, attr, value):
        if attr == 'name':
            super(Album, self).__setattr__('slug', slugify(value))

        super(Album, self).__setattr__(attr, value)

    def __repr__(self):
        return '<Album (%s)>' % self.name


class Track(db.Model):
    """
    """

    __tablename__ = 'tracks'

    pk = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.Unicode(256), unique=True, nullable=False)
    title = db.Column(db.String(128))
    bitrate = db.Column(db.Integer)
    file_size = db.Column(db.Integer)
    length = db.Column(db.Integer)
    number = db.Column(db.Integer)
    slug = db.Column(db.String(), nullable=False)

    album_pk = db.Column(db.Integer, db.ForeignKey('albums.pk'))
    artist_pk = db.Column(db.Integer, db.ForeignKey('artists.pk'))

    def __init__(self, path):
        if type(path) not in (unicode, str, file):
            raise ValueError('Invalid parameter for Track. Path or File '
                             'expected, got %s' % type(path))

        _path = path
        if isinstance(path, file):
            _path = path.name

        self.set_path(_path)
        self._id3r = None

    def __setattr__(self, attr, value):
        if attr == 'title':
            super(Track, self).__setattr__('slug', slugify(value))

        super(Track, self).__setattr__(attr, value)

    def get_path(self):
        if self.path:
            return self.path.encode('utf-8')

        return None

    def set_path(self, path):
        if path != self.get_path():
            self.path = path
            if os.path.exists(self.get_path()):
                self.file_size = self.get_id3_reader().size
                self.bitrate = self.get_id3_reader().bitrate
                self.length = self.get_id3_reader().length
                self.number = self.get_id3_reader().track_number
                self.title = self.get_id3_reader().title

    def get_id3_reader(self):
        """Returns an object with the ID3 info reader.
        """
        if not getattr(self, '_id3r', None):
            self._id3r = ID3Manager(self.get_path())

        return self._id3r

    def __repr__(self):
        return "<Track('%s')>" % self.title
