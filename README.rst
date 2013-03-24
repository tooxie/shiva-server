=====
Shiva
=====

Dinosaurs will slowly die.


License
=======

Please read the LICENSE file distributed with this software.


What is Shiva?
==============

* An API to your music.
* A music player.
* A music collection organizer.


Prerequisites
=============

If you want Shiva to automatically fetch artists' images from Last.FM while
indexing you are going to need an API key. You can get one at
http://www.last.fm/api/account/create

This makes the whole indexing slower because issues a request on a per-album
and per-artist basis, but does a lot of work automatically for you.


Installation
============

* Get the source:

  .. code:: sh

      $ git clone https://github.com/tooxie/shiva-server.git
      $ cd shiva-server

* Install dependencies:

  .. code:: sh

      $ pip install -r requirements.pip

* Rename shiva/config/local.py.example to local.py:

  .. code:: sh

      $ cp shiva/config/local.py.example shiva/config/local.py

* Edit it and configure the directories to scan for music.

  + See `Scanning directories`_ for more info.

* Add shiva to the PYTHONPATH:

  .. code:: sh

      $ export PYTHONPATH=$PYTHONPATH:`pwd`

* Create the database:

  .. code:: sh

      $ python -c "from shiva.app import db; db.create_all()"

* Run the indexer:

  .. code:: sh

      $ python indexer.py

* Run the server:

  .. code:: sh

      $ python shiva/app.py

* Go to ``http://127.0.0.1:5000/<resource>`` (see `Resources`_).


----------------
Using virtualenv
----------------

Usually is a good idea to use virtualenv to keep each project isolated and
avoid dependency conflicts. To do so you should follow the following steps
after cloning the source and before installing the requirements:

* Create the virtual environment:

  .. code:: sh

      $ virtualenv venv

* Activate it:

  .. code:: sh

      $ source ./venv/bin/activate

Then continue with the installation process as described previously.


-----------------
Indexer arguments
-----------------

The indexer receives the following command line arguments.

* ``--lastfm``
* ``--nometadata``

If you set the ``--lastfm`` flag Shiva will retrieve artist and album images
from Last.FM, but for this to work you need to get an API key (see
`Prerequisites`_) and include it in your ``local.py`` config file.

The ``--nometadata`` option saves dummy tracks with only path information,
ignoring the file's metadata. This means that album and artists will not be
saved.

If both flags are set, ``--nometadata`` will take precedence and ``--lastfm``
will be ignored.


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

    MediaDir(root='/srv/http', dirs=('/music', '/songs),
             url='http://localhost:8080/')

Given that configuration Shiva will scan the directories ``/srv/http/music``
and ``/srv/http/songs`` for media files, but they will be served through
``http://localhost:8080/music/`` and ``http://localhost:8080/songs/``.

If just a dir is provided Shiva will serve it through the same instance. This
is **NOT** recommended, but is useful for developing.

.. code:: python

    MediaDir('/home/fatmike/music')

For more information, check the source of `shiva/media.py`.


Client
======

* `Shiva-Client <https://github.com/tooxie/shiva-client>`_

A web-based front-end built as a single page application using HTML5
technologies. It includes its own test web server so you need not to install
one.

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
        "download_uri": "/artist/3/download",
        "id": 3
    }


Fields
------

* ``download_uri``: The URI to download this artist's tracks. *(NOT IMPLEMENTED)*
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
  + ``facebook_tour_dates_ur``l: URI to BandsInTown's Facebook app for this
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
        "download_uri": "/album/9/download",
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
* ``download_uri``: The URI to download this album. (NOT IMPLEMENTED)
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
            "download_uri": "/album/12/download",
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
            "download_uri": "/album/27/download",
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

Example response for the request ``GET /track/484``:

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
        "stream_uri": "http://localhost:8080/nofx-pump_up_the_valuum/04. Dinosaurs Will Die.mp3"

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
* ``stream_uri``: The URI to access the file, according to the MEDIA_DIRS setting.


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
            "stream_uri": "http://localhost:8080/ftd-2003-sofa_so_good/01 For The Day - Pay Cheque (Heritage II).mp3"
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
            "stream_uri": "http://localhost:8080/ftd-2003-sofa_so_good/02 For The Day - In Your Dreams.mp3"
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
            "stream_uri": "http://localhost:8080/flip-keep_rockin/flip-01-shapes.mp3",
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
            "stream_uri": "http://localhost:8080/flip-keep_rockin/flip-02-stucked_to_the_ground.mp3",
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
        "text": "When i came to this world mother told me\r what was right and what was wrong\r while dad explained me that\r religion, country and flag were things i must respect\r \r So, i decided\r to be political correct\r and a good child\r but then, I realized\r that nothing has changed since then...\r \r my family never told me\r why 30.000 people died in the '70's?\r where was the god\r that they promised me\r he was gonna take me to paradise?\r \r and why those children cry\r behind those war planes\r and those war guns\r oh, please father,\r i don't wanna be part of this...",
        "source_uri": "http://lyrics.com/eterna-inocencia/my-family/",
        "id": 6,
        "uri": "/lyrics/6"
    }


Fields
------

* ``id``: The object's ID.
* ``source_uri``: The URI where the lyrics were fetched from.
* ``text``: The lyric's text.
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
were found or ``False`` otherwise. It must also store the lyrics in
``self.lyrics`` and the URL where they fetched from in ``self.source``. That's
where Shiva looks for the information.

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
        "download_uri": "/artist/2/download",
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
                "download_uri": "/album/2/download",
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
                        "stream_uri": "http://localhost:5000/track/27/download",
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
                        "stream_uri": "http://localhost:5000/track/28/download",
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
        "download_uri": "/artist/3/download",
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


Assumptions
===========

For the sake of simplicity many assumptions were made that will eventually be
worked on and improved/removed.

* Only music files. No videos.

  + Actually, only MP3 files.

* No users.

  + Therefore, no customization.
  + And no privacy (You can still use
    `htpasswd <https://httpd.apache.org/docs/2.2/programs/htpasswd.html>`_,
    thou.)

* No uploading of files.
* No update of ID3 info when DB info changes.


Known issues
============

* The ID3 reader doesn't always detect the bit rate correctly. Seems like a
  common issue to many libraries, at least the ones I tried.


Wish list
=========

* Index your music and videos.

  + Which formats? Ogg Vorbis? FLAC? WAV?

* Batch-edit ID3 tags.
* Download your songs in batch.
* Users.

  + Favourite artists.
  + Playlists.

* Share your music with your friends.
* Share your music with your friends' servers.
* Listen to your friends' music.
* They can also upload their music.
* Stream audio and video. (Radio mode)
* Set up a radio and collaboratively pick the music.
* Tabs.


Disclaimer
==========

Remember that when using this software you must comply with your country's
laws. You and only you will be held responsible for any law infringement
resulting from the misuse of this software.

That said. Have fun.


Why Shiva?
==========

https://en.wikipedia.org/wiki/Shiva_crater
