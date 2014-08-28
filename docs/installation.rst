Installation
============

Before installing shiva there are some dependencies that you have to take care
of.


Prerequisites
-------------

You are going to need:

* ffmpeg
* libxml C headers
* python headers
* sqlite (optional)

If you want Shiva to automatically fetch artists' images from Last.FM while
indexing you are going to need an API key. You can get one at
http://www.last.fm/api/account/create

This makes the whole indexing slower because issues a request on a per-album
and per-artist basis, but does a lot of work automatically for you.

By default Shiva uses a SQLite database, but this can be overriden.

To install all the dependencies on Debian (and derivatives)::

    sudo apt-get install libxml2-dev libxslt-dev ffmpeg python-dev sqlite

If at some point of the installation process you get the error:

.. code::

    /usr/bin/ld: cannot find -lz

You also need the package ``lib32z1-dev``

On Mac OS X with `homebrew <http://mxcl.github.com/homebrew/>`_ you can get the
libxml headers with::

    brew install libxml2 libxslt

On Mac OS X sqlite should come pre-installed. If it's not::

    brew install sqlite


Installing from source
----------------------

* Get the source::

.. code:: sh

    $ git clone https://github.com/tooxie/shiva-server.git
    $ cd shiva-server

* Create and activate your virtalenv (highly recommended)::

.. code:: sh

    $ virtualenv .virtualenv
    $ source .virtualenv/bin/activate

* Install::

.. code:: sh

    $ python setup.py develop

* Rename shiva/config/local.py.example to local.py::

.. code:: sh

    $ cp shiva/config/local.py.example shiva/config/local.py

See `Configuration`_ for more info.

* Edit it and configure the directories to scan for music.

  + See `Scanning directories`_ for more info.

* Run the indexer::

.. code:: sh

  $ shiva-indexer

* Run the file server::

.. code:: sh

  $ shiva-fileserver

* Run the server in a different console::

.. code:: sh

  $ shiva-server

* Point your browser to a Resource, like: http://127.0.0.1:9002/artists (See
  `Base Resources`_)


Installing using pip
--------------------

You can install Shiva through ``pip``, running the following command:

.. code:: sh

    $ pip install shiva

That will automatically download and install Shiva and all its dependencies.

**Note:** This will install the latest release, which may contain bugs and lack
some features. It is highly recommended that you install the latest development
version, following the manual installation guide above.
