.. |buildstatus| image:: https://secure.travis-ci.org/tooxie/shiva-server.png?branch=master
    :alt: Build status
    :target: http://travis-ci.org/tooxie/shiva-server
.. |testcoverage| image:: https://coveralls.io/repos/tooxie/shiva-server/badge.png
    :alt: Test coverage
    :target: https://coveralls.io/r/tooxie/shiva-server

=====
Shiva
=====

Dinosaurs will slowly die.

|buildstatus| |testcoverage|


License
=======

Please read the LICENSE file distributed with this software.


What is Shiva?
==============

The Mozilla Hacks blog kindly published a nice article that explains the ideas
that inspire this software:
`Shiva: More than a RESTful API to your music collection
<https://hacks.mozilla.org/2013/03/shiva-more-than-a-restful-api-to-your-music-collection/>`_


Prerequisites
=============

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


Installation
============

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

See `Configuring`_ for more info.

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
  `Resources`_)


Installation using pip
======================

You can install Shiva through ``pip``, running the following command:

.. code:: sh

    $ pip install shiva

That will automatically download and install Shiva and all its dependencies.

**Note:** This will install the latest release, which may contain bugs and lack
some features. It is highly recommended that you install the latest development
version, following the manual installation guide above.


-----------
Configuring
-----------

Shiva looks for config files in the following places:

* ``config/local.py`` relative to the directory where Shiva is installed.
* If an environment variable ``$SHIVA_CONFIG`` is set, then is assumed to be
  pointing to a config file.
* ``$XDG_CONFIG_HOME/shiva/config.py`` which defauls to
  ``$HOME/.config/shiva/config.py``.

If all 3 files exist, then all 3 will be read and overriden in that same order,
so ``$XDG_CONFIG_HOME/shiva/config.py`` will take precedence over
``config/local.py``.


DEBUG
-----

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


Indexing
========

The indexer receives the following command line arguments.

* ``--lastfm``
* ``--nometadata``
* ``--reindex``
* ``--write-every=<num>``

If you set the ``--lastfm`` flag Shiva will retrieve artist and album images
from Last.FM, but for this to work you need to get an API key (see
`Prerequisites`_) and include it in your ``local.py`` config file.

The ``--nometadata`` option saves dummy tracks with only path information,
ignoring the file's metadata. This means that albums and artists will not be
saved, but indexing will be as fast as it gets.

If both flags are set, ``--nometadata`` will take precedence and ``--lastfm``
will be ignored.

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


----------------------
Restricting extensions
----------------------

If you want to limit the extensions of the files to index, just add the
following config to your ``local.py`` file:

.. code:: python

    ALLOWED_FILE_EXTENSIONS = ('mp3', 'ogg')

That way only 'mp3' and 'ogg' files will be indexed.


--------------------
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


Clients
=======

* `Shiva-Client <https://github.com/tooxie/shiva-client>`_

A web-based front-end built as a single page application using HTML5
technologies. It includes its own test web server so you don't need to install
one.

* `Shiva4J <https://github.com/instant-solutions/shiva4j>`_

Java implementation of the Shiva protocol. Runs on android.

* `Shakti <https://github.com/gonz/shakti>`_

A web based client built with AngularJS.


------------------
Wish you were here
------------------

Or you can also build your own client and put your own ideas into practice. I
encourage you to do so. Build your own music player that meets your exact
needs.

Feel free to issue PRs if you need new functionality in Shiva.


Resources
=========

You have the following resources available:

* ``/artists``
* ``/artist/<int:artist_id>``
* ``/artist/<int:artist_id>/shows``
* ``/albums``
* ``/album/<int:album_id>``
* ``/tracks``
* ``/track/<int:track_id>``
* ``/track/<int:track_id>/lyrics``

And some meta resources:

* ``/random/<str:resource_name>``
* ``/whatsnew``
* ``/clients``
* ``/about``


----------------
Artists Resource
----------------

Example response for the request ``GET /artist/3``:

.. code:: javascript

    {
        "name": "Eterna Inocencia",
        "image": "http://userserve-ak.last.fm/serve/_/8339787/Eterna+Inocencia+Eterna.jpg",
        "uri": "/artist/3",
        "slug": "eterna-inocencia",
        "id": 3
    }


Fields
------

* ``id``: The object's ID.
* ``image``: Link to a photo. (Provided by last.fm)
* ``name``: The artist's name.
* ``slug``: A `slug <https://en.wikipedia.org/wiki/Slug_(web_publishing)#Slug>`_
  of the artist's name.
* ``uri``: The URI of this resource's instance.


--------------
Shows Resource
--------------

Information provided by `BandsInTown <http://www.bandsintown.com/>`_. This is
the only resource that is not cached in the local database given to it's
dynamic nature.

Example response for the request ``GET /artist/1/shows``:

.. code:: javascript

    [
        {
            "other_artists": [
                {
                    "mbid": "5c210861-2ce2-4be3-9307-bbcfc361cc01",
                    "facebook_tour_dates_url": "http://bnds.in/kVwY1Y",
                    "image_url": "http://www.bandsintown.com/Pennywise/photo/medium.jpg",
                    "name": "Pennywise",
                }
            ],
            "artists": [
                {
                    "id": 1,
                    "uri": "/artist/1"
                }
            ],
            "tickets_left": true,
            "title": "Lagwagon @ Commodore Ballroom in Vancouver, Canada",
            "venue": {
                "latitude": "49.2805760",
                "name": "Commodore Ballroom",
                "longitude": "-123.1207430"
            },
            "id": "6041814",
            "datetime": "Thu, 21 Feb 2013 19:00:00 -0000"

        }
    ]


Fields
------

* ``other_artists``: A list with artists that are not in Shiva's database.

  + ``mbid``: MusicBrainz.org ID.
  + ``facebook_tour_dates_url``: URI to BandsInTown's Facebook app for this
    artist.
  + ``image_url``: URI to an image of the artist.
  + ``name``: Name of the artist.

* ``artists``: A list of artist resources.
* ``tickets_left``: A boolean representing the availability (or not) of
  tickets for the concert.
* ``title``: The title of the event.
* ``venue``: A structure identifying the venue where the event takes place.

  + ``latitude``: Venue's latitude.
  + ``name``: Venue's name.
  + ``longitude``: Venue's longitude.

* ``id``: BandsInTown's ID for this event.
* ``datetime``: String representation of the date and time of the show.


Parameters
----------

The Shows resource accepts, optionally, two pairs of parameters:

* ``latitude`` and ``longitude``
* ``country`` and ``city``

By providing one of this two pairs you can filter down the result list only to
a city. If only one of the pair is provided (e.g., only city) will be ignored,
and if both pairs are provided, the coordinates will take precedence.


---------------
Albums Resource
---------------

Example response for the request ``GET /album/9``:

.. code:: javascript

    {
        "artists": [
            {
                "id": 2,
                "uri": "/artist/2"
            },
            {
                "id": 5,
                "uri": "/artist/5"
            }
        ],
        "name": "NOFX & Rancid - BYO Split Series (Vol. III)",
        "year": 2002,
        "uri": "/album/9",
        "cover": "http://userserve-ak.last.fm/serve/300x300/72986694.jpg",
        "id": 9,
        "slug": "nofx-rancid-byo-split-series-vol-iii"
    }


Fields
------

* ``artists``: A list of the artists involved in that record.
* ``cover``: A link to an image of the album's cover. (Provided by last.fm)
* ``id``: The object's ID.
* ``name``: The album's name.
* ``slug``: A `slug <https://en.wikipedia.org/wiki/Slug_(web_publishing)#Slug>`_
  of the album's name.
* ``uri``: The URI of this resource's instance.
* ``year``: The release year of the album.


Filtering
---------

The album list accepts an ``artist`` parameter in which case will filter the
list of albums only to those corresponding to that artist.

Example response for the request ``GET /albums/?artist=7``:

.. code:: javascript

    [
        {
            "artists": [
                {
                    "id": 7,
                    "uri": "/artist/7"
                }
            ],
            "name": "Anesthesia",
            "year": 1995,
            "uri": "/album/12",
            "cover": "http://userserve-ak.last.fm/serve/300x300/3489534.jpg",
            "id": 12,
            "slug": "anesthesia"
        },
        {
            "artists": [
                {
                    "id": 7,
                    "uri": "/artist/7"
                }
            ],
            "name": "Kum Kum",
            "year": 1996,
            "uri": "/album/27",
            "cover": "http://userserve-ak.last.fm/serve/300x300/62372889.jpg",
            "id": 27,
            "slug": "kum-kum"
        }
    ]


--------------
Track Resource
--------------

Example response for the request ``GET /track/510``:

.. code:: javascript

    {

        "number": 4,
        "bitrate": 128,
        "slug": "dinosaurs-will-die",
        "album": {
            "id": 35,
            "uri": "/album/35"
        },
        "title": "Dinosaurs Will Die",
        "artist": {
            "id": 2,
            "uri": "/artist/2"
        },
        "uri": "/track/510",
        "id": 510,
        "length": 180,
        "files": {
            "audio/mp3": "http://localhost:8080/nofx-pump_up_the_valuum/04. Dinosaurs Will Die.mp3",
            "audio/ogg": "/track/510/convert?mimetype=audio%2Fogg"
        }

    }


Fields
------

* ``album``: The album to which this track belongs.
* ``bitrate``: In MP3s this value is directly proportional to the `sound
  quality <https://en.wikipedia.org/wiki/Bit_rate#MP3>`_.
* ``id``: The object's ID.
* ``length``: The length in seconds of the track.
* ``number``: The `ordinal number <https://en.wikipedia.org/wiki/Ordinal_number>`_
  of this track with respect to this album.
* ``slug``: A `slug <https://en.wikipedia.org/wiki/Slug_(web_publishing)#Slug>`_
  of the track's title.
* ``title``: The title of the track.
* ``uri``: The URI of this resource's instance.
* ``files``: A list of URIs to access the files in the different formats,
  according to the MEDIA_DIRS setting.


Filtering
---------

The track listing accepts one of two possible parameters to filter down the
list only to those tracks corresponding to a given ``album`` or ``artist``.


By artist
~~~~~~~~~

Example response for the request ``GET /tracks?artist=16``:

.. code:: javascript

    [
        {
            "number": 1,
            "bitrate": 196,
            "slug": "pay-cheque-heritage-ii",
            "album": {
                "id": 36,
                "uri": "/album/36"
            },
            "title": "Pay Cheque (Heritage II)",
            "artist": {
                "id": 16,
                "uri": "/artist/16"
            },
            "uri": "/track/523",
            "id": 523,
            "length": 189,
            "files": {
                "audio/mp3": "http://localhost:8080/ftd-2003-sofa_so_good/01 For The Day - Pay Cheque (Heritage II).mp3",
                "audio/ogg": "/track/523/convert?mimetype=audio%2Fogg"
            }
        },
        {
            "number": 2,
            "bitrate": 186,
            "slug": "in-your-dreams",
            "album": {
                "id": 36,
                "uri": "/album/36"
            },
            "title": "In Your Dreams",
            "artist": {
                "id": 16,
                "uri": "/artist/16"
            },
            "uri": "/track/531",
            "id": 531,
            "length": 171,
            "files": {
                "audio/mp3": "http://localhost:8080/ftd-2003-sofa_so_good/02 For The Day - In Your Dreams.mp3",
                "audio/ogg": "/track/523/convert?mimetype=audio%2Fogg"
            }
        }
    ]


By album
~~~~~~~~

Example response for the request ``GET /tracks?album=18``:

.. code:: javascript

    [

        {
            "album": {
                "id": 18,
                "uri": "/album/18"
            },
            "length": 132,
            "files": {
                "audio/mp3": "http://localhost:8080/flip-keep_rockin/flip-01-shapes.mp3",
                "audio/ogg": "/track/277/convert?mimetype=audio%2Fogg"
            }
            "number": 1,
            "title": "Shapes",
            "slug": "shapes",
            "artist": {
                "id": 9,
                "uri": "/artist/9"
            },
            "bitrate": 192,
            "id": 277,
            "uri": "/track/277"
        },
        {
            "album": {
                "id": 18,
                "uri": "/album/18"
            },
            "length": 118,
            "files": {
                "audio/mp3": "http://localhost:8080/flip-keep_rockin/flip-02-stucked_to_the_ground.mp3",
                "audio/ogg": "/track/281/convert?mimetype=audio%2Fogg"
            }
            "number": 2,
            "title": "Stucked to The Ground",
            "slug": "stucked-to-the-ground",
            "artist": {
                "id": 9,
                "uri": "/artist/9"
            },
            "bitrate": 192,
            "id": 281,
            "uri": "/track/281"
        }
    ]


---------------
Lyrics Resource
---------------

Example response for the request ``GET /track/256/lyrics``:

.. code:: javascript

    {
        "track": {
            "id": 256,
            "uri": "/track/256"
        },
        "source_uri": "http://lyrics.com/eterna-inocencia/my-family/",
        "id": 6,
        "uri": "/lyrics/6"
    }


Fields
------

* ``id``: The object's ID.
* ``source_uri``: The URI where the lyrics were fetched from.
* ``track``: The track for which the lyrics are.
* ``uri``: The URI of this resource's instance.


Adding more lyric sources
-------------------------

Everytime you request a lyric, Shiva checks if there's a lyric associated with
that track in the database. If it's there it will immediately retrieve it,
otherwise will iterate over a list of scrapers, asking each one of them if they
can fetch it. This list is in your local config file and looks like this:

.. code:: python

    SCRAPERS = {
        'lyrics': (
            'modulename.ClassName',
        ),
    }

This will look for a class ``ClassName`` in ``shiva/lyrics/modulename.py``. If
more scrapers are added, each one of them is called sequentially, until one of
them finds the lyrics and the rest are not executed.


Adding scrapers
~~~~~~~~~~~~~~~

If you want to add your own scraper just create a file under the lyrics
directory, let's say ``mylyrics.py`` with this structure:

.. code:: python

    from shiva.lyrics import LyricScraper

    class MyLyricsScraper(LyricScraper):
        """ Fetches lyrics from mylyrics.com """

        def fetch(self, artist, title):
            # Magic happens here

            if not lyrics:
                return False

            self.lyrics = lyrics
            self.source = lyrics_url

            return True

And then add it to the scrapers list:

.. code:: python

    SCRAPERS = {
        'lyrics': (
            'modulename.ClassName',
            'mylyrics.MyLyricsScraper',
        ),
    }

Remember that the ``fetch()`` method has to return ``True`` in case the lyrics
were found or ``False`` otherwise. It must also store the URL where they were
fetched from in ``self.source``. That's where Shiva looks for the information.

Shiva will **not** store the actual lyrics, only the URI where the lyric was
found.

For more details check the source of the other scrapers.


-------------------------
The ``fulltree`` modifier
-------------------------

The three main resources accept a ``fulltree`` parameter when retrieving an
instance.
Those are:

* ``/artist/<int:artist_id>``
* ``/album/<int:album_id>``
* ``/track/<int:track_id>``

Whenever you set ``fulltree`` to any value that evaluates to ``True`` (i.e.,
any string except ``'false'`` and ``'0'``) Shiva will include not only the
information of the object you are requesting, but also the child objects.

Here's an example response for the request ``GET /artist/2?fulltree=true``:

.. code:: javascript

    {
        "name": "Eterna Inocencia",
        "image": "http://userserve-ak.last.fm/serve/_/8339787/Eterna+Inocencia+Eterna.jpg",
        "uri": "/artist/2",
        "events_uri": null,
        "id": 2,
        "slug": "eterna-inocencia",
        "albums": [
            {
                "artists": [
                    {
                        "id": 2,
                        "uri": "/artist/2"
                    }
                ],
                "name": "Tomalo Con Calma EP",
                "year": 2002,
                "uri": "/album/2",
                "cover": "http://spe.fotolog.com/photo/30/54/51/alkoldinamita/1230537010699_f.jpg",
                "id": 2,
                "slug": "tomalo-con-calma-ep",
                "tracks": [
                    {
                        "album": {
                            "id": 2,
                            "uri": "/album/2"
                        },
                        "length": 161,
                        "files": {
                            "audio/mp3": "http://127.0.0.1:8001/eterna_inocencia/tomalo-con-calma.mp3",
                            "audio/ogg": "/track/27/convert?mimetype=audio%2Fogg"
                        }
                        "number": 0,
                        "title": "02 - Rio Lujan",
                        "slug": "02-rio-lujan",
                        "artist": {
                            "id": 2,
                            "uri": "/artist/2"
                        },
                        "bitrate": 192,
                        "id": 27,
                        "uri": "/track/27"
                    },
                    {
                        "album": {
                            "id": 2,
                            "uri": "/album/2"
                        },
                        "length": 262,
                        "files": {
                            "audio/mp3": "http://127.0.0.1:8001/eterna_inocencia/estoy-herido-en-mi-interior.mp3",
                            "audio/ogg": "/track/28/convert?mimetype=audio%2Fogg"
                        }
                        "number": 0,
                        "title": "03 - Estoy herido en mi interior",
                        "slug": "03-estoy-herido-en-mi-interior",
                        "artist": {
                            "id": 2,
                            "uri": "/artist/2"
                        },
                        "bitrate": 192,
                        "id": 28,
                        "uri": "/track/28"
                    },
                ]
            }
        ]
    }


Using ``fulltree`` on tracks
----------------------------

The behaviour on a track resource is a little different. In the previous
example tracks are the leaves of the tree, but when the fulltree of a track is
requested then all the scraped resources are also included, like lyrics.

This is not the default behaviour to avoid DoS'ing scraped websites when
fetching the complete discography of an artist.


----------
Pagination
----------

All the listings are not paginated by default. Whenever you request a list of
either *artists*, *albums* or *tracks* the server will retrieve every possible
result unless otherwise specified.

It is possible to paginate results by passing the ``page_size`` and the
``page`` parameters to the resource. They must both be present and be positive
integers. If not,  they will both be ignored and the whole set of elements
will be retrieved.

An example request is ``GET /artists?page_size=10&page=3``.


--------------------------
Using slugs instead of IDs
--------------------------

It is possible to use slugs instead of IDs when requesting an specific
resource. It will work the exact same way because slugs, as IDs, are unique. An
example on the ``/artist`` resource:

Example response for the request ``GET /artist/eterna-inocencia``:

.. code:: javascript

    {
        "name": "Eterna Inocencia",
        "image": "http://userserve-ak.last.fm/serve/_/8339787/Eterna+Inocencia+Eterna.jpg",
        "uri": "/artist/3",
        "slug": "eterna-inocencia",
        "id": 3
    }


-------------------
Uniqueness of slugs
-------------------

Slugs are generated from the following fields:

* ``Artist.name``
* ``Album.name``
* ``Track.title``

If the slug clashes with an existing one, then a hyphen and a unique ID will be
appended to it. Due to the possibility of `using slugs instead of IDs`_, if an
slug results in a numeric string a hyphen and a unique ID will be appended to
remove the ambiguity.


----------------
Random resources
----------------

You can request a random instance of a given resource for *artists*, *albums*
or *tracks*. To do so you need to issue a GET request on one of the following
resources:

* ``/random/artist``
* ``/random/album``
* ``/random/track``

They all will return a consistent structure containing ``id`` and ``uri``, as
in this example response for the request ``GET /random/artist``:

.. code:: javascript

    {
        "id": 3,
        "uri": "/artist/3"
    }

You will have to issue another request to obtain the details of the instance.


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


--------------
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


--------------------
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


------------------
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


What's new?
===========

There's a special resource that lets you query the database to retrieve all the
resources older than a given date, at the same time:

.. code:: html

    /whatsnew?since=YYYYMMDD

This will return an object with the following format:

.. code:: javascript

    {
        "artists": [],
        "albums": [
            {
                "id": 10,
                "uri": "/album/10"
            }
        ],
        "tracks": [
            {
                "id": 121,
                "uri": "/track/121"
            },
            {
                "id": 122,
                "uri": "/track/122"
            }
        ],
    }


Cross Origin Resource Sharing
=============================

`CORS <http://de.wikipedia.org/wiki/Cross-Origin_Resource_Sharing>`_ support is
disabled by default because it's a browser-specific feature, and Shiva doesn't
assume that the clients are browsers.

To enable CORS you have to set the following in your ``local.py`` file:

.. code:: python

    CORS_ENABLED = True

Now Shiva will add the following header to each response:

.. code:: html

    Access-Control-Allow-Origin: *
    Access-Control-Allow-Headers: Accept, Content-Type, Origin, X-Requested-With

If you want to limit it to a single origin, then define a tuple with the
accepted domains:

.. code:: python

    CORS_ALLOWED_ORIGINS = ('napster.com', 'slsknet.org')

Or simply a string:

.. code:: python

    CORS_ALLOWED_ORIGINS = 'napster.com'

When a domain (or a tuple of domains) is defined, Shiva will check the request
against it. If they match, a header is added:

.. code:: html

    Access-Control-Allow-Origin: http://napster.com


Want to contribute?
===================

There are many ways you can contribute:

* File bug reports.
* Implement new features.
* Build your own client.
* Write documentation.
* Write tests.
* Talk about Shiva.

  + Write an article.
  + Give a talk.

* Use it!

If you build a client or write an article about Shiva, let us know and we'll
include it in our documentation.


------------
Sending code
------------

If you want to implement a new feature or fix a bug, remember that every PR
that you issue must:

* Strictly follow the `PEP8 <http://www.python.org/dev/peps/pep-0008/>`_.
* Include documentation, if applicable.

  + Detailed documentation of the new feature.
  + Update old documentation for functionality changes.

* Include tests.
* Not break previous tests.

The `CI tool <https://travis-ci.org/tooxie/shiva-server>`_ will check for most
of this, so make sure the build passes.


Bug Reports
===========

Please report bugs, recommend enhancements or ask questions in our
`issue tracker <https://github.com/tooxie/shiva-server/issues>`_. Before
reporting bugs please make sure of the following:

* The bug was not previously reported.
* You have the latest version installed.
* The bug is not actually a feature.


Assumptions
===========

For the sake of simplicity many assumptions were made that will eventually be
worked on and improved/removed.

* Only music files. No videos. No images.
* No users.

  + Therefore, no customization.
  + And no privacy.

* No uploading of files.
* No update of files' metadata when DB info changes.


Wish list
=========

This is a (possible incomplete) list of ideas that may be eventually
implemented. With time we will see which of them make sense (or not) and work
on them (or not). We may add things that are not documented here as well.

* Index also images and videos.
* Batch-edit ID3 tags.
* Download your tracks in batch.
* Users.

  + Favourite artists.
  + Playlists.
  + Play count.

* Share your music with your friends.
* Share your music with your friends' servers.
* Listen to your friends' music.
* They can also upload their music.
* Stream audio and video. (Radio mode)
* Set up a radio and collaboratively pick the music. (Would this belong to
  Shiva or to another service consuming Shiva's API?)
* Tabs.


Disclaimer
==========

Remember that when using this software you must comply with your country's
laws. You and only you will be held responsible for any law infringement
resulting from the misuse of this software.

That said. Have fun.


Why Shiva?
==========

Shiva is the name of the `crater <https://en.wikipedia.org/wiki/Shiva_crater>`_
that would have been created by the
`K-Pg event <https://en.wikipedia.org/wiki/Cretaceous%E2%80%93Paleogene_extinction_event>`_
that extincted the `dinosaurs <https://www.youtube.com/watch?v=dlAeN3Qxlvc>`_.
