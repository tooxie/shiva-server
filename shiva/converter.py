# -*- coding: utf-8 -*-
import os
import subprocess
import urllib

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

    CONVERSION_URI = '/tracks/%s/convert?%s'

    def __init__(self, track, mimetype):
        self.track = track
        self.fullpath = None
        self.uri = None
        self.mimetype = None
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

    def get_dest_directory(self):
        """
        Retrieves the path on which a track's duplicates, i.e. that same track
        converted to other formats, will be stored.

        In this case they will be stored along the original track, in the same
        directory.

        """

        file_path = os.path.dirname(self.track.path)

        # If we are asked for the destination path of the original file, we
        # don't need to append the extension to the path.
        if self.track.path.endswith(self.mimetype.extension):
            return file_path

        path = os.path.join(file_path, self.mimetype.extension)

        return path

    def mkdir(self, path):
        if not os.path.exists(path):
            os.mkdir(path)

    def get_dest_filename(self):
        filename = os.path.basename(self.track.path)
        if '.' in filename and not filename.startswith('.'):
            filename = '.'.join(filename.split('.')[0:-1])

        return '.'.join((filename, self.mimetype.extension))

    def get_dest_fullpath(self):
        if self.fullpath:
            return self.fullpath

        directory = self.get_dest_directory()
        filename = self.get_dest_filename()

        return os.path.join(directory, filename)

    def get_conversion_uri(self):
        mimetype = urllib.urlencode({'mimetype': str(self.mimetype)})
        uri = self.CONVERSION_URI % (self.track.pk, mimetype)

        return ''.join((app.config.get('SERVER_URI') or '', uri))

    def get_uri(self):
        if self.converted_file_exists():
            self.uri = self.get_file_uri()
        else:
            self.uri = self.get_conversion_uri()

        return self.uri

    def get_file_uri(self):
        for mdir in app.config['MEDIA_DIRS']:
            return mdir.urlize(self.get_dest_fullpath())

    def convert(self):
        path = self.get_dest_fullpath()
        self.mkdir(os.path.dirname(path))
        if self.converted_file_exists():
            return path

        # Don't do app.config.get('FFMPEG_PATH', 'ffmpeg'). That will cause an
        # error when FFMPEG_PATH is set to None or empty string.
        ffmpeg = app.config.get('FFMPEG_PATH') or 'ffmpeg'
        cmd = [ffmpeg, '-i', self.track.path, '-aq', '60', '-acodec',
               self.mimetype.acodec, path]

        proc = subprocess.call(cmd)

        return path

    def converted_file_exists(self):
        return os.path.exists(self.get_dest_fullpath())
