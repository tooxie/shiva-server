# -*- coding: utf-8 -*-
from flask.ext.restful import fields, marshal
from flask import current_app as app, request


class InstanceURI(fields.String):
    def __init__(self, base_uri):
        self.base_uri = base_uri

    def output(self, key, obj):
        return '/%s/%i' % (self.base_uri, obj.pk)


class StreamURI(fields.Raw):
    """ Only tracks can be streamed """

    def output(self, key, obj):
        for mdir in app.config['MEDIA_DIRS']:
            stream_uri = mdir.urlize(getattr(obj, 'path', ''))
            if stream_uri:
                return stream_uri

        return '%strack/%s/download.%s' % (request.url_root, obj.pk,
                                           obj.get_extension())


class DownloadURI(InstanceURI):
    def output(self, key, obj):
        uri = super(DownloadURI, self).output(key, obj)

        return '%s/download.mp3' % uri


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


class Boolean(fields.Raw):
    def output(self, key, obj):
        return bool(super(Boolean, self).output(key, obj))
