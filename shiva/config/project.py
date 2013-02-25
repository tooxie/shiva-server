# -*- coding: utf-8 -*-
from shiva.converter import Converter

DEBUG = True

SQLALCHEMY_DATABASE_URI = 'sqlite:///shiva.db'
CONVERTER_CLASS = Converter
MIMETYPES = {
    'audio': {
        'audio/mp3': {
            'codec': 'libmp3lame',
            'extension': 'mp3'
        },
    },
}
