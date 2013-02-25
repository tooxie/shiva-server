# -*- coding: utf-8 -*-
import os
import re
from random import random
from hashlib import md5

import translitcodec

PUNCT_RE = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def slugify(text):
    """Generates an ASCII-only slug."""
    if not text:
        return ''
    result = []
    text = text
    for word in PUNCT_RE.split(text.lower()):
        word = word.encode('translit/long')
        if word:
            result.append(word)

    return unicode(u'-'.join(result))


def randstr(length=None):
    if length < 1:
        return ''

    digest = md5(str(random())).hexdigest()

    if length:
        return digest[:length]

    return digest


def _import(class_path):
    bits = class_path.split('.')
    mod_name = '.'.join(bits[:-1])
    cls_name = bits[-1]

    mod = __import__(mod_name, None, None, cls_name)

    return getattr(mod, cls_name)


class ID3Manager(object):
    def __init__(self, mp3_path):
        import eyed3  # FIXME: Replace ASAP

        self.mp3_path = mp3_path
        self.reader = eyed3.load(mp3_path)

        if not self.reader.tag:
            self.reader.tag = eyed3.id3.Tag()
            self.reader.tag.track_num = (None, None)

        if self.reader.tag.album is None:
            self.reader.tag.album = u''

        if self.reader.tag.artist is None:
            self.reader.tag.artist = u''

        self.reader.tag.save(mp3_path)

    def __getattribute__(self, attr):
        _super = super(ID3Manager, self)
        try:
            _getter = _super.__getattribute__('get_%s' % attr)
        except AttributeError:
            _getter = None
        if _getter:
            return _getter()

        return super(ID3Manager, self).__getattribute__(attr)

    def __setattr__(self, attr, value):
        value = value.strip() if isinstance(value, (str, unicode)) else value
        _setter = getattr(self, 'set_%s' % attr, None)
        if _setter:
            _setter(value)

        super(ID3Manager, self).__setattr__(attr, value)

    def is_valid(self):
        if not self.reader.path:
            return False

        return True

    def get_path(self):
        return self.mp3_path

    def same_path(self, path):
        return path == self.mp3_path

    def get_artist(self):
        return self.reader.tag.artist.strip()

    def set_artist(self, name):
        self.reader.tag.artist = name
        self.reader.tag.save()

    def get_album(self):
        return self.reader.tag.album.strip()

    def set_album(self, name):
        self.reader.tag.album = name
        self.reader.tag.save()

    def get_release_year(self):
        rdate = self.reader.tag.release_date
        return rdate.year if rdate else None

    def set_release_year(self, year):
        self.release_date.year = year
        self.reader.tag.save()

    def get_bitrate(self):
        return self.reader.info.bit_rate[1]

    def get_length(self):
        return self.reader.info.time_secs

    def get_track_number(self):
        return self.reader.tag.track_num[0]

    def get_title(self):
        if not self.reader.tag.title:
            _title = raw_input('Song title: ').decode('utf-8').strip()
            self.reader.tag.title = _title
            self.reader.tag.save()

        return self.reader.tag.title

    def get_size(self):
        """Computes the size of the mp3 file in filesystem.
        """
        return os.stat(self.reader.path).st_size


        return os.stat(self.reader.path).st_size
