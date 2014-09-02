Format conversion
=================

No matter in which format files were indexed, it is possible to convert tracks
to serve them in different formats. For this you are going to need ``ffmpeg``
installed in your system.

If you have ``fmpeg`` compiled but not installed, you can give Shiva the path
to the binary in a setting, in this format:

.. code:: python

    FFMPEG_PATH = '/usr/bin/ffmpeg'

You will notice that track objects contain a ``files`` attribute:

.. code:: javascript

    {
        "id": 510,
        "uri": "/track/510",
        "files": {
            "audio/mp3": "http://localhost:8080/nofx-pump_up_the_valuum/04. Dinosaurs Will Die.mp3",
            "audio/ogg": "/track/510/convert?mimetype=audio%2Fogg"
        }
    }

In that attribute you will find a list of all the supported formats. That list
is generated from the ``MIMETYPES`` setting (see `The MIMETYPES config`_). Just
follow the link of the format you need and Shiva will convert it if necessary
and serve it for you. As a client, that's all you care about.

But you may have noticed that the URI for the ``audio/ogg`` format goes through
Shiva. This is because the file has not been yet converted, once you call that
URI, Shiva will convert the file on the fly, cache it and redirect to the file.
The next time the same track is requested, if the file exists it will be served
through the file server instead of Shiva:

.. code:: javascript

    {
        "id": 510,
        "uri": "/track/510",
        "files": {
            "audio/mp3": "http://localhost:8080/nofx-pump_up_the_valuum/04. Dinosaurs Will Die.mp3",
            "audio/ogg": "http://localhost:8080/nofx-pump_up_the_valuum/04. Dinosaurs Will Die.ogg"
        }
    }

It's completely transparent for the client. If you want an OGG file, you just
follow the "audio/ogg" URI blindly, and you will get your file. The first time
will take a little longer, though.


Absolute paths
--------------

If you need absolute paths for your ``/convert`` URIs, just set the
``SERVER_URI`` setting in your local config, it will be prepended to all the
URIs:

.. code:: python

    SERVER_URI = 'http://127.0.0.1:9002'

Example output:

.. code:: javascript

    {
        "files": {
            "audio/mp3": "http://127.0.0.1:8001/flip-keep_rockin/flip-10-away_from_the_sun.mp3",
            "audio/ogg": "http://127.0.0.1:9002/track/1/convert?mimetype=audio%2Fogg"
        },
        "album": {
            "id": 1,
            "uri": "http://127.0.0.1:9002/album/1"
        },
        "length": 168,
        "number": 10,
        "title": "Away From The Sun",
        "slug": "away-from-the-sun",
        "artist": {
            "id": 1,
            "uri": "http://127.0.0.1:9002/artist/1"
        },
        "bitrate": 192000,
        "id": 1,
        "uri": "http://127.0.0.1:9002/track/1"
    }

Remember to leave out trailing slashes.


Your converter sucks
--------------------

So, you don't want to use ``ffmpeg``, or you want to call it with different
parameters, or chache files differently. That's ok, I won't take it personally.

To overwrite the Converter class to use, just define it in your config:

.. code:: python

    from shiva.myconverter import MyBetterConverter

    CONVERTER_CLASS = MyBetterConverter

One option is to extend ``shiva.converter.Converter`` and overwrite the methods
that offend you.

The other option is to write a completely new Converter class. If you do so,
make sure to have at least the following 3 methods:

* ``__init__(Track track, (str, MimeType) mimetype)``: Constructor accepting a
  path to a file and a mimetype, which could be a string in the form of
  'type/subtype', or a MimeType instance.
* ``convert()``: Converts to a different format.
* ``get_uri()``: Retrieves the URI to the converted file.

The ``shiva.resources.ConvertResource`` class makes use of them.


The MimeType class
------------------

All mimetypes are represented by a ``shiva.media.MimeType`` class. The
constructor receives the following parameters:

* ``type``: Would be ``audio`` in ``audio/ogg``.
* ``subtype``: Would be ``ogg`` in ``audio/ogg``.
* ``extension``: The extension that converted files should have.
* ``acodec`` and/or ``vcodec``: The codecs used by ``Converter.convert()``.
  Find out the available codecs running:

.. code:: sh

    $ ffmpeg -codecs


The MIMETYPES config
--------------------

You will see in your config file:

.. code:: python

    MIMETYPES = (
        MimeType(type='audio', subtype='mp3', extension='mp3',
                 acodec='libmp3lame'),
        MimeType(type='audio', subtype='ogg', extension='ogg',
                 acodec='libvorbis'),
    )

Keep in mind that an invalid MimeType in this config will raise an
``InvalidMimeTypeError`` exception.
