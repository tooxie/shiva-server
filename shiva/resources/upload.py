# -*- coding: utf-8 -*-
"""
This module contains the default file upload handler. When a file is uploaded
it is given to this class, which is responsible for storing it and returning
the path to it. If you need to change how or where uploaded files are stored,
extend this class and overload its methods.
"""
import hashlib
import os
import shutil
import tempfile

from flask import current_app as app
from slugify import slugify

from shiva.exceptions import (InvalidFileTypeError, MetadataManagerReadError,
                              NoUploadPathConfigError)
from shiva.utils import MetadataManager


class UploadHandler(object):
    """
    This class will handle the upload of new tracks. First it will be saved in
    a temporary location in order to be examined by the metadata manager. Once
    it made sure is a valid track, it will be moved to the final destination
    which consists of a configurable path, plus artist and album name. If the
    track cannot be read as a music file it will be deleted from the file
    system.

    The following config options are used by this class:
        * UPLOAD_PATH
        * UPLOAD_DEFAULT_ARTIST
        * UPLOAD_DEFAULT_ALBUM

    Only the first one, `UPLOAD_PATH` is required and will cause a
    `NoUploadPathConfigError` exception to be thrown if not present.

    Usage:
        >>> from flask import request
        >>> handler = UploadHandler(request.files)
        >>> path = handler.save()

    You can manually call `get_full_path()` at any time to get the final
    destination of the uploaded file.
    """

    def __init__(self, track):
        self.track = track
        self.filename = track.filename
        self.temp_path = self.save_temp()
        self.hash = self.get_hash()

        try:
            self.mdma = MetadataManager(self.temp_path)
        except MetadataManagerReadError, e:
            self.clean()
            raise InvalidFileTypeError(e.message)

        self.artist = self.mdma.artist
        self.album = self.mdma.album

    @property
    def path(self):
        return self.get_full_path()

    def save(self):
        self.move()

        return self.get_full_path()

    def save_temp(self):
        self.tfile = tempfile.NamedTemporaryFile()
        self.tfile.write(self.track.read())

        # self.track.close()

        return self.tfile.name

    def get_hash(self):
        md5 = hashlib.md5(self.track.read())
        self.hash = md5.hexdigest()

        return self.hash

    def move(self):
        # What shall we do with clashing paths? What if the uploaded file
        # exists in the filesystem but has a different hash? Files without
        # metadata will all clash, we need to make sure that they get a random
        # name. Something like 'unknown-xxxxx.mp3' where xxxxx is the hash.
        if not os.path.exists(self.get_full_path()):
            shutil.move(self.temp_path, self.get_full_path())

    def clean(self):
        self.tfile.close()
        try:
            os.unlink(self.get_full_path())
        except OSError:
            pass

    def get_path(self):
        path = ''
        upload_path = app.config.get('UPLOAD_PATH')

        if not upload_path:
            raise NoUploadPathConfigError()

        _artist = app.config.get('UPLOAD_DEFAULT_ARTIST', '')
        _album = app.config.get('UPLOAD_DEFAULT_ALBUM', '')

        artist = slugify(self.mdma.artist) or _artist
        album = slugify(self.mdma.album) or _album

        path = os.path.join(upload_path, artist, album)

        try:
            os.makedirs(path)
        except OSError:  # File exists
            pass

        return path

    def get_filename(self):
        filename = self.filename

        if '.' in filename:
            pieces = filename.split('.')
            ext = pieces[-1]
            filename = '.'.join(pieces[:-1])

        # We slugify the name to remove funny chars like '..' and '/'.
        hashed = '%s-%s' % (slugify(filename), self.hash[:6])
        filename = '.'.join((hashed, ext))

        return filename

    def get_full_path(self):
        return os.path.join(self.get_path(), self.get_filename())
