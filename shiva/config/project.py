# -*- coding: utf-8 -*-
from shiva.converter import Converter
from shiva.resources.upload import UploadHandler
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

# Compress all responses with gzip. Will be ignored in DEBUG mode.
USE_GZIP = True

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

# If you need to change the way uploaded files are handled (e.g. where they are
# stored) extend this class and modify its behaviour. Read the class source for
# more info.
UPLOAD_HANDLER = UploadHandler
# This setting, in addition to MEDIA_DIRS, is used by the converter and the
# file server to know where track files are stored.
UPLOAD_PATH = ''
# The following 2 settings will be appended to UPLOAD_PATH in case the track
# contains no metadata. For more info read the source of the `shiva.upload`
# module.
UPLOAD_DEFAULT_ARTIST = 'unknown'
UPLOAD_DEFAULT_ALBUM = 'unknown'

# Auth
# Time (in seconds) for which the session tokens will be valid. After this time
# the client will have to re-authenticate.
AUTH_EXPIRATION_TIME = 3600  # 1h
ALLOW_ANONYMOUS_ACCESS = True
