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
