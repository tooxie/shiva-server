# -*- coding: utf-8 -*-
from flask.ext.restful import fields, marshal


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


class ForeignKeyField(fields.Raw):
    def __init__(self, foreign_obj, nested):
        self.foreign_obj = foreign_obj
        self.nested = nested

        super(ForeignKeyField, self).__init__()

    def output(self, key, obj):
        _id = getattr(obj, '%s_pk' % key)
        if not _id:
            return None

        obj = self.foreign_obj.query.get(_id)

        return marshal(obj, self.nested)


class AlbumCover(fields.Raw):
    def output(self, key, obj):
        output = super(AlbumCover, self).output(key, obj)
        if not output:
            output = ('http://wortraub.com/wp-content/uploads/2012/07/'
                     'Vinyl_Close_Up.jpg')

        return output
