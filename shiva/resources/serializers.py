# -*- coding: utf-8 -*-
"""
Classes responsible for serializing models into different representations.
"""
from flask import current_app as app
from flask.ext.restful import fields, marshal

from shiva.exceptions import NoModelToSerializeError
from shiva.models import Album, Artist, Track, User
from shiva.resources import fields as custom_fields


class Serializer(object):

    def __init__(self, db_model=None):
        self.db_model = db_model
        self.schema = self.get_schema()
        self.raw_fields = {}

    def to_json(self, recursive=False):
        if self.db_model is None:
            raise NoModelToSerializeError(self.__class__.__name__)

        if recursive:
            for key, serializer in self.get_relationships().iteritems():
                self.update_schema({
                    key: custom_fields.SerializerField(serializer)
                })

        items = marshal(self.db_model, self.schema)

        return self.apply_raw_fields(items)

    def update_schema(self, fields_dict):
        self.schema.update(fields_dict)

    def add_raw_field(self, fields_dict):
        """ A raw field will be added to the resulting json, unmodified. """

        self.raw_fields = fields_dict

    def apply_raw_fields(self, items):
        if type(items) == list:
            for item in items:
                item.update(self.raw_fields)
        else:
            items.update(self.raw_fields)

        return items

    def add_m2m_rel(self, key, db_model, serializer_class):
        serializer = serializer_class(db_model)
        m2m = custom_fields.ManyToManyField(db_model, serializer.get_schema())

        self.update_schema({key: m2m})


class ArtistSerializer(Serializer):

    def get_schema(self):
        return {
            'id': fields.String(attribute='pk'),
            'name': fields.String,
            'slug': fields.String,
            'uri': custom_fields.InstanceURI('artists'),
            'image': fields.String(default=app.config['DEFAULT_ARTIST_IMAGE']),
            'events_uri': fields.String(attribute='events'),
        }

    def get_relationships(self):
        return {
            'albums': AlbumSerializer,
        }


class AlbumSerializer(Serializer):

    def get_schema(self):
        return {
            'id': fields.String(attribute='pk'),
            'name': fields.String,
            'slug': fields.String,
            'year': fields.Integer,
            'uri': custom_fields.InstanceURI('albums'),
            'artists': custom_fields.ManyToManyField(Artist, {
                'id': fields.String(attribute='pk'),
                'uri': custom_fields.InstanceURI('artists'),
            }),
            'cover': fields.String(default=app.config['DEFAULT_ALBUM_COVER']),
        }

    def get_relationships(self):
        return {
            'tracks': TrackSerializer,
        }


class TrackSerializer(Serializer):

    def get_schema(self):
        return {
            'id': fields.String(attribute='pk'),
            'uri': custom_fields.InstanceURI('tracks'),
            'files': custom_fields.TrackFiles,
            'bitrate': fields.Integer,
            'length': fields.Integer,
            'title': fields.String,
            'slug': fields.String,
            'artists': custom_fields.ManyToManyField(Artist, {
                'id': fields.String(attribute='pk'),
                'uri': custom_fields.InstanceURI('artists'),
            }),
            'albums': custom_fields.ManyToManyField(Album, {
                'id': fields.String(attribute='pk'),
                'uri': custom_fields.InstanceURI('albums'),
            }),
            'ordinal': fields.Integer,
        }

    def get_relationships(self):
        return {
            'lyrics': LyricsSerializer,
            # 'tabs': TabsSerializer,
        }


class PlaylistSerializer(Serializer):

    def get_schema(self):
        return {
            'id': fields.String(attribute='pk'),
            'name': fields.String,
            'user': custom_fields.ForeignKeyField(User, {
                'id': fields.String(attribute='pk'),
                'uri': custom_fields.InstanceURI('users'),
            }),
            'read_only': fields.Boolean,
            'creation_date': fields.DateTime,
            'length': fields.Integer,
            'tracks': custom_fields.PlaylistField({
                'id': fields.String(attribute='pk'),
                'uri': custom_fields.InstanceURI('tracks'),
            }),
        }

    # TODO: Playlists' full tree.


class UserSerializer(Serializer):

    def get_schema(self):
        return {
            'id': fields.String(attribute='pk'),
            'display_name': fields.String,
            'creation_date': fields.DateTime,
        }


class LyricsSerializer(Serializer):

    def get_schema(self):
        return {
            'id': fields.Integer(attribute='pk'),
            'uri': custom_fields.InstanceURI('lyrics'),
            'text': fields.String,
            'source_uri': fields.String(attribute='source'),
            'track': custom_fields.ForeignKeyField(Track, {
                'id': fields.Integer(attribute='pk'),
                'uri': custom_fields.InstanceURI('track'),
            }),
        }


class ShowsSerializer(Serializer):

    def get_schema(self):
        return {
            'id': fields.String,
            'artists': custom_fields.ManyToManyField(Artist, {
                'id': fields.Integer(attribute='pk'),
                'uri': custom_fields.InstanceURI('artist'),
            }),
            'other_artists': fields.List(fields.Raw),
            'datetime': fields.DateTime,
            'title': fields.String,
            'tickets_left': Boolean,
            'venue': fields.Nested({
                'latitude': fields.String,
                'longitude': fields.String,
                'name': fields.String,
            }),
        }
