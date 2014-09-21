Configuration
=============

Shiva looks for config files in the following places:

* ``config/local.py`` relative to the directory where Shiva is installed.
* If an environment variable ``$SHIVA_CONFIG`` is set, then is assumed to be
  pointing to a config file.
* ``$XDG_CONFIG_HOME/shiva/config.py`` which defauls to
  ``$HOME/.config/shiva/config.py``.

If all 3 files exist, then all 3 will be read and overriden in that same order,
so ``$XDG_CONFIG_HOME/shiva/config.py`` will take precedence over
``config/local.py``.


SECRET_KEY
----------

It's mandatory that you define a ``SECRET_KEY`` in your local configuration
file, ``shiva-server`` won't start otherwise. However, shiva will suggest you
one which will be based on all printable characters, except for spaces and
quotes. Read the source of ``shiva.utils.randstr`` for more information.

The key will be used to sign the authentication tokens, so make sure that it's
long, random, and securely generated. Don't ever use any 3rd party service for
this.


DEBUG mode
----------

It's possible to load settings specific for debugging. If you have the
following in any of your config files:

.. code:: python

    DEBUG = True

Then Shiva will also try to load this configuration files:

* ``config/debug.py`` relative to the directory where Shiva is installed.
* ``$XDG_CONFIG_HOME/shiva/debug.py`` which defauls to
  ``$HOME/.config/shiva/debug.py``.

In this case ``$XDG_CONFIG_HOME/shiva/debug.py`` will also have precedence over
``config/debug.py``.
