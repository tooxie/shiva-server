# -*- coding: utf-8 -*-
from shiva.media import MediaDir

from os import path

DEBUG = True

PROJECT_ROOT = path.dirname(path.abspath(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///%s/stream.db' % PROJECT_ROOT
SECRET_KEY = '-'  # TODO: Move this option to a file that can be edited in a
                  # per-installation basis.
ACCEPTED_FORMATS = (
    'mp3',
    'ogg',
)
MEDIA_DIRS = (
    # Examples
    # MediaDir(root='/srv/http', dirs=('/music',), url='http://127.0.0.1/'),
    # MediaDir('/home/fatmike/music/shiva'),
)
