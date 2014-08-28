Indexing your music
===================

The indexer receives the following command line arguments.

* ``--lastfm``
* ``--hash``
* ``--nometadata``
* ``--reindex``
* ``--write-every=<num>``

If you set the ``--lastfm`` flag Shiva will retrieve artist and album images
from Last.FM, but for this to work you need to get an API key (see
`Prerequisites`_) and include it in your ``local.py`` config file.

When ``--hash`` is present, Shiva will hash every file using the md5 algorithm,
in order to find duplicates, which will be ignored. Note that this will
decrease indexing speed notably.

The ``--nometadata`` option saves dummy tracks with only path information,
ignoring the file's metadata. This means that albums and artists will not be
saved, but indexing will be as fast as it gets.

If both the ``--nometadata`` and ``--lastfm`` flags are set, ``--nometadata``
will take precedence and ``--lastfm`` will be ignored.

With ``--reindex`` the whole database will be dropped and recreated. Be
careful, all existing information **will be deleted**. If you just want to
update your music collection, run the indexer again **without** the
``--reindex`` option.

The indexer is optimized for performance; hard drive hits, like file reading or
DB queries, are done as few as possible. As a consequence, memory usage is
quite heavy. Keep that in mind when indexing large collections.

To keep memory usage down, you can use the ``--write-every`` parameter. It
receives a number and will write down to disk and clear cache after that many
tracks indexed. If you pass 1, it will completely ignore cache and just write
every track to disk. This has the lowest possible memory usage, but as a
downside, indexing will be much slower.

It's up to you to find a good balance between the size of your music collection
and the available RAM that you have.


Restricting extensions
----------------------

If you want to limit the extensions of the files to index, just add the
following config to your ``local.py`` file:

.. code:: python

    ALLOWED_FILE_EXTENSIONS = ('mp3', 'ogg')

That way only 'mp3' and 'ogg' files will be indexed.


Scanning directories
--------------------

To tell Shiva which directories to scan for music, you will have to configure
your ``shiva/config/local.py`` file. There you will find a ``MEDIA_DIRS``
option where you need to supply ``MediaDir`` objects.

This object allows for media configuration. By instantiating a ``MediaDir``
class you can tell Shiva where to look for the media files and how to serve
those files. It's possible to configure the system to look for files on a
directory and serve those files through a different server.

.. code:: python

    MediaDir(root='/srv/http', dirs=('/music', '/songs'),
             url='http://localhost:8080/')

Given that configuration Shiva will scan the directories ``/srv/http/music``
and ``/srv/http/songs`` for media files, but they will be served through
``http://localhost:8080/music/`` and ``http://localhost:8080/songs/``.

If just a dir is provided you will also need to run the file server, as
mentioned in the installation guide. This is a simple file server, for testing
purposes only. Do **NOT** use in a live environment.

.. code:: python

    MediaDir('/home/fatmike/music')

For more information, check the source of `shiva/media.py`.
