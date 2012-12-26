# -*- coding: utf-8 -*-
import os
from hashlib import md5
import re

import eyed3
from flask import Flask
from flask.ext.restful import (abort, Api, fields, marshal, marshal_with,
                               Resource)
from flask.ext.sqlalchemy import SQLAlchemy

NUM_RE = re.compile('\d')

# Setup {{{
app = Flask(__name__)
DB_PATH = 'shiva.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % DB_PATH
db = SQLAlchemy(app)
api = Api(app)
# }}}


# DB {{{
class Artist(db.Model):
    """
    """

    __tablename__ = 'artists'

    pk = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)

    albums = db.relationship('Album', backref='artist', lazy='dynamic')

    def __repr__(self):
        return '<Artist (%s)>' % self.name


class Album(db.Model):
    """
    """

    __tablename__ = 'albums'

    pk = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)
    year = db.Column(db.Integer)

    tracks = db.relationship('Track', backref='album', lazy='dynamic')
    artist_pk = db.Column(db.Integer, db.ForeignKey('artists.pk'))

    def __repr__(self):
        return '<Album (%s)>' % self.name


class Track(db.Model):
    """
    """

    __tablename__ = 'tracks'

    pk = db.Column(db.Integer, primary_key=True)
    _path = db.Column(db.String(128), unique=True, nullable=False)
    md5_hash = db.Column(db.String(128), unique=True, nullable=False)
    title = db.Column(db.String(128))
    bitrate = db.Column(db.Integer)
    file_size = db.Column(db.Integer)
    length = db.Column(db.Integer)

    album_pk = db.Column(db.Integer, db.ForeignKey('albums.pk'))

    def __init__(self, path):
        if type(path) not in (unicode, str, file):
            raise ValueError('Invalid parameter for Track. Path or File '
                             'expected, got %s' % type(path))

        _path = path
        if isinstance(path, file):
            _path = path.name

        self.path = _path
        self._id3r = None

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        if path != self._path:
            if os.path.exists(path):
                self._path = path
                self.file_size = self.compute_size()
                self.md5_hash = self.compute_hash()
                self.bitrate = self.get_bitrate()
                self.length = self.get_length()
                self.title = self.get_title()

    def get_file(self):
        """Returns the file as a python file object.
        """
        return open(self._path, 'r')

    def compute_hash(self):
        """Computes the MD5 digest for this file.
        """
        track_file = self.get_file()

        return md5(track_file.read()).hexdigest()

    def compute_size(self):
        """Computes the size of a file in filesystem.
        """
        return os.stat(self._path).st_size

    def get_id3_reader(self):
        """Returns an object with the ID3 info reader.
        """
        if not getattr(self, '_id3r', None):
            # TODO: Encapsulate this inside a class
            self._id3r = eyed3.load(self._path)

        return self._id3r

    def get_bitrate(self):
        """Reads the bitrate information from the file.
        """
        bitrate = self.get_id3_reader().info.bit_rate_str

        return ''.join(NUM_RE.findall(bitrate))

    def get_length(self):
        """Computes the length of the track in seconds.
        """
        return self.get_id3_reader().info.time_secs

    def get_title(self):
        """
        """
        return self.get_id3_reader().tag.title

    def __repr__(self):
        return "<Track('%s')>" % self.md5_hash
# }}}


# Fields {{{
class FieldMap(fields.Raw):
    def __init__(self, field_name, formatter):
        self.field_name = field_name
        self.formatter = formatter

    def format(self, value):
        self.formatter(value)

    def output(self, key, obj):
        return getattr(obj, self.field_name)


class InstanceURI(fields.String):
    def __init__(self, base_uri):
        self.base_uri = base_uri

    def output(self, key, obj):
        return '/%s/%i' % (self.base_uri, obj.pk)


class StreamURI(fields.String):
    def output(self, key, obj):
        return '/stream/%i' % obj.pk


class DownloadURI(fields.String):
    def output(self, key, obj):
        return '/download/%i' % obj.pk


class ForeignKeyField(fields.Raw):
    def __init__(self, foreign_obj, nested):
        self.foreign_obj = foreign_obj
        self.nested = nested

        super(ForeignKeyField, self).__init__()

    def output(self, key, obj):
        _id = getattr(obj, '%s_pk' % key)
        obj = db.session.query(self.foreign_obj).get(_id)

        return marshal(obj, self.nested)
# }}}


# Resources {{{
class ArtistResource(Resource):
    """
    """

    route_base = 'artists'
    resource_fields = {
        'id': FieldMap('pk', lambda x: int(x)),
        'name': fields.String,
        'uri': InstanceURI('artist'),
    }

    def get(self, artist_id=None):
        if not artist_id:
            return list(self.get_all())

        return self.get_one(artist_id)

    def get_all(self):
        artists = Artist.query.all()

        for artist in artists:
            yield marshal(artist, self.resource_fields)

    @marshal_with(resource_fields)
    def get_one(self, artist_id):
        artist = Artist.query.get(artist_id)

        if not artist:
            abort(404)

        return artist


class AlbumResource(Resource):
    """
    """

    route_base = 'albums'
    resource_fields = {
        'id': FieldMap('pk', lambda x: int(x)),
        'name': fields.String,
        'year': fields.Integer,
        'uri': InstanceURI('album'),
        'artist': ForeignKeyField(Artist, {
            'id': FieldMap('pk', lambda x: int(x)),
            'uri': InstanceURI('artist'),
        }),
    }

    def get(self, album_id=None):
        if not album_id:
            return list(self.get_all())

        return self.get_one(album_id)

    def get_all(self):
        albums = Album.query.all()

        for album in albums:
            yield marshal(album, self.resource_fields)

    @marshal_with(resource_fields)
    def get_one(self, album_id):
        album = Album.query.get(album_id)

        if not album:
            abort(404)

        return album


class TracksResource(Resource):
    """
    """

    route_base = 'tracks'
    resource_fields = {
        'id': FieldMap('pk', lambda x: int(x)),
        'uri': InstanceURI('track'),
        # 'path': fields.String,
        'stream_uri': StreamURI,
        'download_uri': DownloadURI,
        # 'hash': FieldMap('md5_hash', lambda x: str(x)),
        'bitrate': fields.Integer,
        'length': fields.Integer,
        'title': fields.String,
        'album': ForeignKeyField(Album, {
            'id': FieldMap('pk', lambda x: int(x)),
            'uri': InstanceURI('album'),
        }),
    }

    def get(self, track_id=None):
        if not track_id:
            return list(self.get_all())

        return self.get_one(track_id)

    def get_all(self):
        # TODO: Pagination
        tracks = Track.query.all()

        for track in tracks:
            yield marshal(track, self.resource_fields)

    @marshal_with(resource_fields)
    def get_one(self, track_id):
        track = Track.query.get(track_id)

        if not track:
            abort(404)

        return track


api.add_resource(ArtistResource, '/artists', '/artist/<int:artist_id>',
                 endpoint='artist')
api.add_resource(AlbumResource, '/albums', '/album/<int:album_id>',
                 endpoint='album')
api.add_resource(TracksResource, '/tracks', '/track/<int:track_id>',
                 endpoint='track')
# }}}

if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        db.create_all()
    app.run('0.0.0.0', debug=True)
