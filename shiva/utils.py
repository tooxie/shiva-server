# -*- coding: utf-8 -*-
import os
from random import random
from hashlib import md5
from contextlib import contextmanager


def randstr(length=None):
    """ Generates a random string of the given length. """

    if length < 1:
        return ''

    digest = md5(str(random())).hexdigest()

    if length:
        return digest[:length]

    return digest


def _import(class_path):
    """ Imports a module or class from a string in dot notation. """

    bits = class_path.split('.')
    mod_name = '.'.join(bits[:-1])
    cls_name = bits[-1]

    mod = __import__(mod_name, None, None, cls_name)

    return getattr(mod, cls_name)


@contextmanager
def ignored(*exceptions):
    """Context manager that ignores all of the specified exceptions. This will
    be in the standard library starting with Python 3.4."""
    try:
        yield
    except exceptions:
        pass


class MetadataManager(object):
    """A format-agnostic metadata wrapper around Mutagen.

    This makes reading/writing audio metadata easy across all possible audio
    formats by using properties for the different keys.

    In order to persist changes to the metadata, the ``save()`` method needs to
    be called.

    """
    def __init__(self, filepath):
        self._original_path = filepath
        self.reader = mutagen.File(filepath, easy=True)

    # Static attributes

    VALID_FILE_EXTENSIONS = [
        'asf', 'wma',  # ASF
        'flac',  # FLAC
        'mp4', 'm4a', 'm4b', 'm4p',  # M4A
        'ape',  # Monkey's Audio
        'mp3',  # MP3
        'mpc', 'mp+', 'mpp',  # Musepack
        'spx',  # Ogg Speex
        'ogg', 'oga',  # Ogg Vorbis / Theora
        'tta',  # True Audio
        'wv',  # WavPack
        'ofr',  # OptimFROG
    ]

    # Metadata properties

    @property
    def title(self):
        return self._getter('title')

    @property
    def artist(self):
        """The artist name."""
        return self._getter('artist')

    @artist.setter
    def artist(self, value):
        self.reader['artist'] = value

    @property
    def album(self):
        """The album name."""
        return self._getter('album')

    @album.setter
    def album(self, value):
        self.reader['album'] = value

    @property
    def release_year(self):
        """The album release year."""
        return self._getter('date')

    @release_year.setter
    def release_year(self, value):
        self.reader['year'] = value

    @property
    def track_number(self):
        """The track number."""
        return self._getter('tracknumber')

    @track_number.setter
    def track_number(self, value):
        self.reader['tracknumber'] = value

    @property
    def genre(self):
        """The music genre."""
        return self._getter('genre')

    @genre.setter
    def genre(self, value):
        self.genre = value

    @property
    def length(self):
        """The length of the song in seconds."""
        return int(round(self.reader.info.length))

    @property
    def bitrate(self):
        """The audio bitrate."""
        return self.reader.info.bitrate

    @property
    def sample_rate(self):
        """The audio sample rate."""
        return self.reader.info.sample_rate

    @property
    def filename(self):
        """The file name of this audio file."""
        return os.path.basename(self.reader.filename)

    @property
    def filepath(self):
        """The absolute path to this audio file."""
        return os.path.abspath(self.reader.filename)

    @property
    def origpath(self):
        """The original path with which this class was instantiated. This
        function avoids a call to ``os.path``.  Usually you'll want to use
        either :meth:`.filename` or :meth:`.filepath` instead."""
        return self._original_path

    @property
    def filesize(self):
        """The size of this audio file in the filesystem."""
        return os.stat(self.reader.filename).st_size

    # Helper functions

    def _getter(self, attr, fallback=None):
        """Return the first list item of the specified attribute or fall back
        to a default value if attribute is not available."""
        return self.reader[attr][0] if attr in self.reader else fallback

    def save(self):
        """Save changes to file metadata."""
        self.reader.save()
