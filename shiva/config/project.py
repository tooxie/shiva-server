# -*- coding: utf-8 -*-
from shiva.converter import Converter

DEBUG = True

SQLALCHEMY_DATABASE_URI = 'sqlite:///shiva.db'
ACCEPTED_FORMATS = (
    'mp3',
)
CONVERTER_CLASS = Converter
MIMETYPES = {
    'audio': {
        'audio/mp3': {
            'codec': 'libmp3lame',
            'extension': 'mp3'
        },
        'audio/ogg': {
            'acodec': 'libvorbis',
            'extension': 'ogg'
        },
    },
}
