# FIXME: This is a hack to treat HeaderNotFoundError as a generic read error of
# the metadata manager. It is disgusting. Fix.
from mutagen.mp3 import HeaderNotFoundError as MetadataManagerReadError

class InvalidMimeTypeError(Exception):
    def __init__(self, mimetype):
        msg = "Invalid mimetype '%s'" % str(mimetype)

        super(InvalidMimeTypeError, self).__init__(msg)
