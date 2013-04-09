# -*- coding: utf-8 -*-
import os
import subprocess

from flask import current_app as app

from shiva.exceptions import InvalidMimeTypeError
from shiva.media import MimeType

def get_converter():
    ConverterClass = app.config.get('CONVERTER_CLASS', Converter)

    return ConverterClass


class Converter(object):
    """
    Class responsible for format conversion. Receives the path to a track (as a
    string) and decides where to save the converted files. It also decides
    which external software to use for conversion.

    """

    def __init__(self, path, mimetype):
        self.path = path
        self.mimetypes = self.get_mimetypes()
        self.set_mimetype(mimetype)

    def get_mimetypes(self):
        """
        Returns the list of mimetypes that the system supports, provided by the
        MIMETYPES setting.

        """

        return app.config.get('MIMETYPES', [])

    def set_mimetype(self, mimetype):
        """
        Sets the mimetype or raises an InvalidMimeTypeError exception if it's
        not found in the settings.
        """

        mimetype_object = None
        if issubclass(mimetype.__class__, MimeType):
            mimetype_object = mimetype
        else:
            for _mime in self.mimetypes:
                if hasattr(_mime, 'matches') and callable(_mime.matches):
                    if _mime.matches(mimetype):
                        mimetype_object = _mime

        if mimetype_object:
            self.fullpath = None
            self.uri = None
            self.mimetype = mimetype_object
        else:
            raise InvalidMimeTypeError(mimetype)

    def get_dest_directory(self, mime=None):
        """
        Retrieves the path on which a track's duplicates, i.e. that same track
        converted to other formats, will be stored.

        In this case they will be stored along the original track, in the same
        directory.

        """

        return os.path.dirname(self.path)

    def get_dest_filename(self):
        filename = os.path.basename(self.path)
        filename = '.'.join(filename.split('.')[0:-1])

        return '.'.join((filename, self.mimetype.extension))

    def get_dest_fullpath(self):
        if self.fullpath:
            return self.fullpath

        directory = self.get_dest_directory()
        filename = self.get_dest_filename()
        self.fullpath = os.path.join(directory, filename)

        return self.fullpath

    def get_dest_uri(self):
        if self.uri:
            return self.uri

        for mdir in app.config['MEDIA_DIRS']:
            path = mdir.urlize(self.get_dest_fullpath())
            if path:
                self.uri = path

        return self.uri

    def convert(self):
        path = self.get_dest_fullpath()
        if self.exists():
            return path

        # Don't do app.config.get('FFMPEG_PATH', 'ffmpeg'). That will cause an
        # error when FFMPEG_PATH is set to None or empty string.
        ffmpeg = app.config.get('FFMPEG_PATH') or 'ffmpeg'
        cmd = [ffmpeg, '-i', self.path, '-aq', '60', '-acodec',
               self.mimetype.acodec, path]

        proc = subprocess.call(cmd)

        return path

    def exists(self):
        return os.path.exists(self.get_dest_fullpath())
