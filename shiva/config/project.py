# -*- coding: utf-8 -*-
from shiva.converter import Converter
from shiva.media import MimeType

DEBUG = True

SQLALCHEMY_DATABASE_URI = 'sqlite:///shiva.db'
ACCEPTED_FORMATS = (
    'mp3',
)
MIMETYPES = (
    MimeType(type='audio', subtype='mp3', extension='mp3',
             acodec='libmp3lame'),
    MimeType(type='audio', subtype='ogg', extension='ogg',
             acodec='libvorbis'),
)
CONVERTER_CLASS = Converter
DEFAULT_ALBUM_COVER = ('http://wortraub.com/wp-content/uploads/2012/07/'
                       'Vinyl_Close_Up.jpg')
DEFAULT_ARTIST_IMAGE = 'http://www.super8duncan.com/images/band_silhouette.jpg'

# https://en.wikipedia.org/wiki/Cross-origin_resource_sharing
CORS_ENABLED = False
# CORS_ALLOWED_ORIGINS accepts the following values:
# The string '*' to allow all origins
# An specific domain: 'google.com'
# A tuple of strings to allow multiple domains: ('google.com', 'napster.com')
CORS_ALLOWED_ORIGINS = '*'

# Allow the deletion of objects through the REST interface. If this is set to
# True, anyone with access will be able to delete objects from the database. It
# won't delete files from the FS, though.
ALLOW_DELETE = False
