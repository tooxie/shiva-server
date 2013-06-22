# -*- coding: utf-8 -*-


class MetadataManagerReadError(Exception):
    pass


class InvalidMimeTypeError(Exception):
    def __init__(self, mimetype):
        msg = "Invalid mimetype '%s'" % str(mimetype)

        super(InvalidMimeTypeError, self).__init__(msg)


class NoConfigFoundError(Exception):
    def __init__(self, *args, **kwargs):
        msg = ('No configuration file found. Please define one:\n'
               '\t* config/local.py\n'
               '\t* Set the environment variable $SHIVA_CONFIG pointing to a '
               'config file.\n'
               '\t* $XDG_CONFIG_HOME/shiva/config.py which defaults to \n'
               '\t  $HOME/.config/shiva/config.py')

        super(NoConfigFoundError, self).__init__(msg)
