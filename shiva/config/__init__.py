# -*- coding: utf-8 -*-
"""
There are 3 types of settings.
1) Project. Stays the same for every installation.
2) Local. Specific to each instance of the project.
3) Debug. Applies for debugging. Forbidden for production use.
"""
import os

from flask import Config as FlaskConfig

from shiva.config import project
from shiva.exceptions import NoConfigFoundError
from shiva.utils import ignored


class Configurator(object):
    """
    Object that takes care of loading the different configurations from the
    different sources. There are 3 types of settings:
        * Project: The basic set of settings needed by the system. These are
          shipped with Shiva.
        * Local: Specific to each instance, useful for overwriting system
          settings. Some of them must be defined before running Shiva, like the
          DB URI.
        * Debug: This setting will only be loaded if ``DEBUG`` is set to True
          in the local settings.

    There are also 3 different places where Shiva looks for this config files:
        * A ``local.py`` file inside the ``config/`` directory, relative to
          Shiva.
        * The ``$SHIVA_CONFIG`` environment variable. It's assumed to be
          pointing to a file (not a dir) if exists.
        * The ``$XDG_CONFIG_HOME/shiva/config.py`` file. If
          ``$XDG_CONFIG_HOME`` is not set, defaults to ``$HOME/.config``, as
          defined by the `XDG Base Directory Specification
          <http://standards.freedesktop.org/basedir-spec/basedir-spec-latest\
.html>`_.
    """

    def __init__(self):
        self._config = FlaskConfig('')

        # project
        _project = self.load_project()

        # local
        _xdg_config = self.from_xdg_config()
        _env = self.from_env()
        _local = self.from_local()

        # debug
        _debug = self.load_debug()

        self.extract_conf(self._config)

        if not (_xdg_config or _env or _local):
            raise NoConfigFoundError

    def load_project(self):
        return self._config.from_object(project)

    def get_xdg_path(self):
        default_config_home = os.path.join(os.getenv('HOME'), '.config')

        return os.getenv('XDG_CONFIG_HOME') or default_config_home

    def from_xdg_config(self):
        local_py = os.path.join(self.get_xdg_path(), 'shiva/config.py')

        if not os.path.exists(local_py):
            return False

        return self._config.from_pyfile(local_py)

    def from_env(self):
        if not os.getenv('SHIVA_CONFIG'):
            return False

        return self._config.from_envvar('SHIVA_CONFIG')

    def from_local(self):
        with ignored(ImportError):
            self._config.from_object('shiva.config.local')

            return True

        return False

    def load_debug(self):
        if not self._config.get('DEBUG'):
            return False

        loaded = False
        with ignored(ImportError):
            from shiva.config import debug

            loaded = self._config.from_object(debug)

        debug_py = os.path.join(self.get_xdg_path(), 'shiva/debug.py')
        if not os.path.exists(debug_py):
            return False

        return self._config.from_pyfile(debug_py) or loaded

    def extract_conf(self, *args):
        """
        Receives one or more objects, iterates over their elements, extracts
        all the uppercase properties and injects them into the Configurator
        object.
        """
        for obj in args:
            for key in dir(obj):
                if key.isupper():
                    setattr(self, key, getattr(obj, key))

            if hasattr(obj, 'iterkeys') and callable(getattr(obj, 'iterkeys')):
                for key in obj.iterkeys():
                    if key.isupper():
                        setattr(self, key, obj[key])
