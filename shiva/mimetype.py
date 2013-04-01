# -*- coding: utf-8 -*-
from flask import current_app as app


class InvalidMimeTypeError(Exception):
    pass


class MimeType(object):
    """Represents a valid mimetype. Holds information like the codecs to be
    used when converting.

    """

    def __init__(self, mimetype=None):
        self.acodec = None
        self.extension = None
        self.vcodec = None

        if mimetype:
            self.set_mimetype(mimetype)

    def set_mimetype(self, mimetype):
        """ Sets the mimetype or raises an InvalidMimeTypeError exception if
        the selected mimetype is not found in the MIMETYPES config.

        """

        self.name = mimetype
        _mimetype = app.config['MIMETYPES'].get('audio', {}).get(mimetype)

        if not _mimetype:
            raise InvalidMimeTypeError('Mimetype "%s" is not valid' % mimetype)

        self.extension = _mimetype['extension']
        self.acodec = _mimetype['acodec']

    def get_audio_codec(self):
        return self.acodec
