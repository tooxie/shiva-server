# -*- coding: utf-8 -*-
from shiva.media import MediaDir

from os import path

DEBUG = True

PROJECT_ROOT = path.dirname(path.abspath(__file__))[:-len('/settings')]
SQLALCHEMY_DATABASE_URI = 'sqlite:///%s/stream.db' % PROJECT_ROOT
ACCEPTED_FORMATS = (
    'mp3',
    'ogg',
)
