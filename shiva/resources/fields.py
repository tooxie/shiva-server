# -*- coding: utf-8 -*-
from flask import current_app as app
from flask.ext.restful import fields, marshal

from shiva.converter import get_converter
from shiva.media import get_mimetypes
from shiva.models import TrackPlaylistRelationship


class InstanceURI(fields.String):
    def __init__(self, base_uri):
        server_uri = app.config.get('SERVER_URI') or ''
        self.base_uri = '/'.join((server_uri, base_uri))

    def output(self, key, obj):
        return '/'.join((self.base_uri, str(obj.pk)))


class TrackFiles(fields.Raw):
    """
    Returns a list of files, one for each available mediatype, for a given
    track.

    """

    def output(self, key, track):
        ConverterClass = get_converter()
        paths = {}

        for mimetype in get_mimetypes():
            converter = ConverterClass(track, mimetype)
            paths[str(mimetype)] = {
                'needs_conversion': not converter.converted_file_exists(),
                'uri': converter.get_uri(),
            }

        return paths


class ManyToManyField(fields.Raw):
    def __init__(self, foreign_obj, nested):
        self.foreign_obj = foreign_obj
        self.nested = nested

        super(ManyToManyField, self).__init__()

    def output(self, key, obj):
        items = list()
        for item in getattr(obj, key):
            items.append(marshal(item, self.nested))

        return items


class PlaylistField(fields.Raw):
    """
    This Field understands the linked list in which the playlist are
    structured. Besides from fetching all the tracks it iterates over the items
    finding the right index for each.
    """

    def __init__(self, nested):
        self.nested = nested

        super(PlaylistField, self).__init__()

    def output(self, key, obj):
        items = list(TrackPlaylistRelationship.query.filter_by(playlist=obj))
        output = []
        prev = None
        index = 0
        while len(items):
            x = 0
            for r_track in items:
                if r_track.previous_track == prev:
                    output.append(self.marshal(r_track, index))
                    del(items[x])
                    prev = r_track
                    index += 1

                    break

                x += 1

        return output

    def marshal(self, r_track, index):
        item = marshal(r_track, self.nested)
        item['index'] = index

        return item


class ForeignKeyField(fields.Raw):
    def __init__(self, foreign_obj, nested):
        self.nested = nested

        super(ForeignKeyField, self).__init__()

    def output(self, key, obj):
        _obj = getattr(obj, '%s' % key)

        return marshal(_obj, self.nested)


class Boolean(fields.Raw):
    def output(self, key, obj):
        return bool(super(Boolean, self).output(key, obj))
