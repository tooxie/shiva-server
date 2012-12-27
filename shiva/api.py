# -*- coding: utf-8 -*-
import os
from hashlib import md5
import re

from flask import Flask, Response, request
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
    image = db.Column(db.String(256))

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
    cover = db.Column(db.String(256))

    tracks = db.relationship('Track', backref='album', lazy='dynamic')
    artist_pk = db.Column(db.Integer, db.ForeignKey('artists.pk'))

    def __repr__(self):
        return '<Album (%s)>' % self.name


class Track(db.Model):
    """
    """

    __tablename__ = 'tracks'

    pk = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.Unicode(256), unique=True, nullable=False)
    md5_hash = db.Column(db.String(128), unique=True, nullable=False)
    title = db.Column(db.String(128))
    bitrate = db.Column(db.Integer)
    file_size = db.Column(db.Integer)
    length = db.Column(db.Integer)
    number = db.Column(db.Integer)

    album_pk = db.Column(db.Integer, db.ForeignKey('albums.pk'))

    def __init__(self, path):
        if type(path) not in (unicode, str, file):
            raise ValueError('Invalid parameter for Track. Path or File '
                             'expected, got %s' % type(path))

        _path = path
        if isinstance(path, file):
            _path = path.name

        self.set_path(_path)
        self._id3r = None

    def get_path(self):
        if self.path:
            return self.path.encode('utf-8')

        return None

    def set_path(self, path):
        if path != self.get_path():
            self.path = path
            if os.path.exists(self.get_path()):
                self.file_size = self.compute_size()
                self.bitrate = self.get_bitrate()
                self.length = self.get_length()
                self.number = self.get_number()
                self.title = self.get_title()

                # Leave this for last, get_title() may change file's contents.
                self.md5_hash = self.compute_hash()

    def get_file(self):
        """Returns the file as a python file object.
        """
        return open(self.get_path(), 'r')

    def compute_hash(self):
        """Computes the MD5 digest for this file.
        """
        track_file = self.get_file()

        return md5(track_file.read()).hexdigest()

    def compute_size(self):
        """Computes the size of a file in filesystem.
        """
        return os.stat(self.get_path()).st_size

    def get_id3_reader(self):
        """Returns an object with the ID3 info reader.
        """
        if not getattr(self, '_id3r', None):
            import eyed3  # FIXME: Replace ASAP
            # TODO: Encapsulate this inside a class
            self._id3r = eyed3.load(self.get_path())

        if not self._id3r.tag:
            self._id3r.tag = eyed3.id3.Tag()
            self._id3r.tag.save(self._id3r.path)

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

    def get_number(self):
        """
        """
        return self.get_id3_reader().tag.track_num[0]

    def get_title(self):
        """
        """
        id3r = self.get_id3_reader()

        if not id3r.tag.title:
            id3r.tag.title = raw_input('Song title: ').decode('utf-8').strip()
            id3r.tag.save()

        return id3r.tag.title

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


class StreamURI(InstanceURI):
    def output(self, key, obj):
        uri = super(StreamURI, self).output(key, obj)

        return '%s/stream' % uri


class DownloadURI(InstanceURI):
    def output(self, key, obj):
        uri = super(DownloadURI, self).output(key, obj)

        return '%s/download' % uri


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
        'download': DownloadURI('artist'),
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
        'download': DownloadURI('album'),
    }

    def get(self, album_id=None):
        if not album_id:
            return list(self.get_all())

        return self.get_one(album_id)

    def get_all(self):
        artist_pk = request.args.get('artist')
        if artist_pk:
            albums = Album.query.filter_by(artist_pk=artist_pk)
        else:
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
        'path': fields.String,  # TODO: Reconsider
        # 'stream_uri': StreamURI,
        'download_uri': DownloadURI('tracks'),
        'hash': FieldMap('md5_hash', lambda x: str(x)),  # TODO: Reconsider
        'bitrate': fields.Integer,
        'length': fields.Integer,
        'title': fields.String,
        'album': ForeignKeyField(Album, {
            'id': FieldMap('pk', lambda x: int(x)),
            'uri': InstanceURI('album'),
        }),
        'number': fields.Integer,
        'download': DownloadURI('track'),
    }

    def get(self, track_id=None):
        if not track_id:
            return list(self.get_all())

        return self.get_one(track_id)

    # TODO: Pagination
    def get_all(self):
        album_pk = request.args.get('album')
        artist_pk = request.args.get('artist')
        if album_pk:
            tracks = Track.query.filter_by(album_pk=album_pk)
        elif artist_pk:
            qs_album = Album.query.filter_by(artist_pk=artist_pk)
            tracks = Track.query.join(qs_album)
        else:
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

# Routes {{{
@app.route('/track/<int:track_id>/download.<ext>')
def download(track_id, ext):
    """
    """
    if ext != 'mp3':
        raise NotImplementedError

    track = db.session.query(Track).get(track_id)
    track_file = open(track.get_path(), 'r')
    filename_header = (
        'Content-Disposition', 'attachment; filename="%s.mp3"' % track.title
    )

    return Response(response=track_file.read(), mimetype='audio/mpeg',
            headers=[filename_header])
# }}}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
