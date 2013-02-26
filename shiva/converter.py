# -*- coding: utf-8 -*-
import os
import subprocess

from flask import current_app as app

def get_converter():
    ConverterClass = app.config.get('CONVERTER_CLASS', Converter)

    return ConverterClass


class Converter(object):
    """
    Class responsible for format conversion. Receives the path to a track (not
    a Track object) and decides where to save the converted files. It also
    decides which external software to use for conversion.

    """

    def __init__(self, path):
        self.path = path
        self.mimetypes = self.get_mimetypes()

    def get_mimetypes(self):
        """
        Returns the list of mimetypes that the system supports, provided by the
        MIMETYPES setting.

        """

        return app.config.get('MIMETYPES', {}).get('audio', {})

    def get_dest_directory(self, mime=None):
        """
        Retrieves the path on which a track's duplicates, i.e. that same track
        converted to other formats, will be stored.

        In this case they will be stored along the original track, in the same
        directory.

        """

        return os.path.dirname(self.path)

    def get_dest_filename(self, mimetype):
        filename = os.path.basename(self.path)

        return '%s.%s' % (filename[:-4], mimetype['extension'])

    def get_dest_fullpath(self, mimetype):
        directory = self.get_dest_directory()
        filename = self.get_dest_filename(mimetype)

        return os.path.join(directory, filename)

    def get_dest_uri(self, mimetype):
        for mdir in app.config['MEDIA_DIRS']:
            path = mdir.urlize(self.get_dest_fullpath(mimetype))
            if path:
                return path

    def get_paths(self):
        for mimetype, mimeinfo in self.mimetypes.iteritems():
            yield self.get_dest_fullpath(mimetype)

    def convert_to(self, mimetype):
        path = self.get_dest_fullpath(mimetype)
        cmd = ['ffmpeg', '-i', self.path, '-acodec', mimetype['codec'], path]

        print(''.join(cmd))

        proc = subprocess.call(cmd)

        return path

    def convert_all(self):
        """
        Converts to all the mimetypes defined in the config if files don't
        exist already.

        """

        for mimetype, mimeinfo in self.mimetypes.iteritems():
            if not self.exists_for_mimetype(mimeinfo):
                self.convert_to(mimeinfo)

    def exists_for_mimetype(self, mimetype):
        return os.path.exists(self.get_dest_fullpath(mimetype))
