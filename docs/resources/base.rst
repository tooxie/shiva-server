Base Resources
==============

You have the following resources available:

* ``/artists``
* ``/artists/<int:artist_id>``
* ``/artists/<int:artist_id>/shows``
* ``/albums``
* ``/albums/<int:album_id>``
* ``/tracks``
* ``/tracks/<int:track_id>``
* ``/tracks/<int:track_id>/lyrics``

And some meta resources:

* ``/random/<str:resource_name>``
* ``/whatsnew``
* ``/clients``
* ``/about``


/artists
--------

Example response for the request ``GET /artists/3``:

.. code:: javascript

    {
        "name": "Eterna Inocencia",
        "image": "http://userserve-ak.last.fm/serve/_/8339787/Eterna+Inocencia+Eterna.jpg",
        "uri": "/artists/3",
        "slug": "eterna-inocencia",
        "id": 3
    }


Fields
~~~~~~

* ``id``: The object's ID.
* ``image``: Link to a photo. (Provided by last.fm)
* ``name``: The artist's name.
* ``slug``: A `slug <https://en.wikipedia.org/wiki/Slug_(web_publishing)#Slug>`_
  of the artist's name.
* ``uri``: The URI of this resource's instance.


/artists/<int:id>/shows
~~~~~~~~~~~~~~~~~~~~~~~
-----------------------

Information provided by `BandsInTown <http://www.bandsintown.com/>`_. This is
the only resource that is not cached in the local database given to it's
dynamic nature.

Example response for the request ``GET /artists/1/shows``:

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
                    "uri": "/artists/1"
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
~~~~~~

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
~~~~~~~~~~

The Shows resource accepts, optionally, two pairs of parameters:

* ``latitude`` and ``longitude``
* ``country`` and ``city``

By providing one of this two pairs you can filter down the result list only to
a city. If only one of the pair is provided (e.g., only city) will be ignored,
and if both pairs are provided, the coordinates will take precedence.


/albums
-------

Example response for the request ``GET /albums/9``:

.. code:: javascript

    {
        "artists": [
            {
                "id": 2,
                "uri": "/artists/2"
            },
            {
                "id": 5,
                "uri": "/artists/5"
            }
        ],
        "name": "NOFX & Rancid - BYO Split Series (Vol. III)",
        "year": 2002,
        "uri": "/albums/9",
        "cover": "http://userserve-ak.last.fm/serve/300x300/72986694.jpg",
        "id": 9,
        "slug": "nofx-rancid-byo-split-series-vol-iii"
    }


Fields
~~~~~~

* ``artists``: A list of the artists involved in that record.
* ``cover``: A link to an image of the album's cover. (Provided by last.fm)
* ``id``: The object's ID.
* ``name``: The album's name.
* ``slug``: A `slug <https://en.wikipedia.org/wiki/Slug_(web_publishing)#Slug>`_
  of the album's name.
* ``uri``: The URI of this resource's instance.
* ``year``: The release year of the album.


Filtering
~~~~~~~~~

The album list accepts an ``artist`` parameter in which case will filter the
list of albums only to those corresponding to that artist.

Example response for the request ``GET /albums/?artist=7``:

.. code:: javascript

    [
        {
            "artists": [
                {
                    "id": 7,
                    "uri": "/artists/7"
                }
            ],
            "name": "Anesthesia",
            "year": 1995,
            "uri": "/albums/12",
            "cover": "http://userserve-ak.last.fm/serve/300x300/3489534.jpg",
            "id": 12,
            "slug": "anesthesia"
        },
        {
            "artists": [
                {
                    "id": 7,
                    "uri": "/artists/7"
                }
            ],
            "name": "Kum Kum",
            "year": 1996,
            "uri": "/albums/27",
            "cover": "http://userserve-ak.last.fm/serve/300x300/62372889.jpg",
            "id": 27,
            "slug": "kum-kum"
        }
    ]


/tracks
-------

Example response for the request ``GET /tracks/510``:

.. code:: javascript

    {

        "number": 4,
        "bitrate": 128,
        "slug": "dinosaurs-will-die",
        "album": {
            "id": 35,
            "uri": "/albums/35"
        },
        "title": "Dinosaurs Will Die",
        "artist": {
            "id": 2,
            "uri": "/artists/2"
        },
        "uri": "/tracks/510",
        "id": 510,
        "length": 180,
        "files": {
            "audio/mp3": "http://localhost:8080/nofx-pump_up_the_valuum/04. Dinosaurs Will Die.mp3",
            "audio/ogg": "/tracks/510/convert?mimetype=audio%2Fogg"
        }

    }


Fields
~~~~~~

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


Filtering by artist
~~~~~~~~~~~~~~~~~~~

Example response for the request ``GET /tracks?artist=16``:

.. code:: javascript

    [
        {
            "number": 1,
            "bitrate": 196,
            "slug": "pay-cheque-heritage-ii",
            "album": {
                "id": 36,
                "uri": "/albums/36"
            },
            "title": "Pay Cheque (Heritage II)",
            "artist": {
                "id": 16,
                "uri": "/artists/16"
            },
            "uri": "/tracks/523",
            "id": 523,
            "length": 189,
            "files": {
                "audio/mp3": "http://localhost:8080/ftd-2003-sofa_so_good/01 For The Day - Pay Cheque (Heritage II).mp3",
                "audio/ogg": "/tracks/523/convert?mimetype=audio%2Fogg"
            }
        },
        {
            "number": 2,
            "bitrate": 186,
            "slug": "in-your-dreams",
            "album": {
                "id": 36,
                "uri": "/albums/36"
            },
            "title": "In Your Dreams",
            "artist": {
                "id": 16,
                "uri": "/artists/16"
            },
            "uri": "/tracks/531",
            "id": 531,
            "length": 171,
            "files": {
                "audio/mp3": "http://localhost:8080/ftd-2003-sofa_so_good/02 For The Day - In Your Dreams.mp3",
                "audio/ogg": "/tracks/523/convert?mimetype=audio%2Fogg"
            }
        }
    ]


Filtering by album
~~~~~~~~~~~~~~~~~~

Example response for the request ``GET /tracks?album=18``:

.. code:: javascript

    [

        {
            "album": {
                "id": 18,
                "uri": "/albums/18"
            },
            "length": 132,
            "files": {
                "audio/mp3": "http://localhost:8080/flip-keep_rockin/flip-01-shapes.mp3",
                "audio/ogg": "/tracks/277/convert?mimetype=audio%2Fogg"
            }
            "number": 1,
            "title": "Shapes",
            "slug": "shapes",
            "artist": {
                "id": 9,
                "uri": "/artists/9"
            },
            "bitrate": 192,
            "id": 277,
            "uri": "/tracks/277"
        },
        {
            "album": {
                "id": 18,
                "uri": "/albums/18"
            },
            "length": 118,
            "files": {
                "audio/mp3": "http://localhost:8080/flip-keep_rockin/flip-02-stucked_to_the_ground.mp3",
                "audio/ogg": "/tracks/281/convert?mimetype=audio%2Fogg"
            }
            "number": 2,
            "title": "Stucked to The Ground",
            "slug": "stucked-to-the-ground",
            "artist": {
                "id": 9,
                "uri": "/artists/9"
            },
            "bitrate": 192,
            "id": 281,
            "uri": "/tracks/281"
        }
    ]


/tracks/<int:id>/lyrics
-----------------------

Example response for the request ``GET /tracks/256/lyrics``:

.. code:: javascript

    {
        "track": {
            "id": 256,
            "uri": "/tracks/256"
        },
        "source_uri": "http://lyrics.com/eterna-inocencia/my-family/",
        "id": 6,
        "uri": "/lyrics/6"
    }


Fields
~~~~~~

* ``id``: The object's ID.
* ``source_uri``: The URI where the lyrics were fetched from.
* ``track``: The track for which the lyrics are.
* ``uri``: The URI of this resource's instance.


Adding more lyric sources
~~~~~~~~~~~~~~~~~~~~~~~~~

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


The ``fulltree`` modifier
-------------------------

The three main resources accept a ``fulltree`` parameter when retrieving an
instance.
Those are:

* ``/artists/<int:artist_id>``
* ``/albums/<int:album_id>``
* ``/tracks``
* ``/tracks/<int:track_id>``

Whenever you set ``fulltree`` to any value that evaluates to ``True`` (i.e.,
any string except ``'false'`` and ``'0'``) Shiva will include not only the
information of the object you are requesting, but also the child objects.

Here's an example response for the request ``GET /artists/2?fulltree=true``:

.. code:: javascript

    {
        "name": "Eterna Inocencia",
        "image": "http://userserve-ak.last.fm/serve/_/8339787/Eterna+Inocencia+Eterna.jpg",
        "uri": "/artists/2",
        "events_uri": null,
        "id": 2,
        "slug": "eterna-inocencia",
        "albums": [
            {
                "artists": [
                    {
                        "id": 2,
                        "uri": "/artists/2"
                    }
                ],
                "name": "Tomalo Con Calma EP",
                "year": 2002,
                "uri": "/albums/2",
                "cover": "http://spe.fotolog.com/photo/30/54/51/alkoldinamita/1230537010699_f.jpg",
                "id": 2,
                "slug": "tomalo-con-calma-ep",
                "tracks": [
                    {
                        "album": {
                            "id": 2,
                            "uri": "/albums/2"
                        },
                        "length": 161,
                        "files": {
                            "audio/mp3": "http://127.0.0.1:8001/eterna_inocencia/tomalo-con-calma.mp3",
                            "audio/ogg": "/tracks/27/convert?mimetype=audio%2Fogg"
                        }
                        "number": 0,
                        "title": "02 - Rio Lujan",
                        "slug": "02-rio-lujan",
                        "artist": {
                            "id": 2,
                            "uri": "/artists/2"
                        },
                        "bitrate": 192,
                        "id": 27,
                        "uri": "/tracks/27"
                    },
                    {
                        "album": {
                            "id": 2,
                            "uri": "/albums/2"
                        },
                        "length": 262,
                        "files": {
                            "audio/mp3": "http://127.0.0.1:8001/eterna_inocencia/estoy-herido-en-mi-interior.mp3",
                            "audio/ogg": "/tracks/28/convert?mimetype=audio%2Fogg"
                        }
                        "number": 0,
                        "title": "03 - Estoy herido en mi interior",
                        "slug": "03-estoy-herido-en-mi-interior",
                        "artist": {
                            "id": 2,
                            "uri": "/artists/2"
                        },
                        "bitrate": 192,
                        "id": 28,
                        "uri": "/tracks/28"
                    },
                ]
            }
        ]
    }


Using ``fulltree`` on tracks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The behaviour on a track resource is a little different. In the previous
example tracks are the leaves of the tree, but when the full tree of a track is
requested then all the scraped resources are also included, like lyrics.

This is not the default behaviour to avoid DoS'ing scraped websites when
fetching the complete discography of an artist.

Note that if you request the list of tracks with ``fulltree``, only the related
resources will be included (i.e.: artists and albums) but not the scraped ones.


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


Using slugs instead of IDs
--------------------------

It is possible to use slugs instead of IDs when requesting an specific
resource. It will work the exact same way because slugs, as IDs, are unique. An
example on the ``/artist`` resource:

Example response for the request ``GET /artists/eterna-inocencia``:

.. code:: javascript

    {
        "name": "Eterna Inocencia",
        "image": "http://userserve-ak.last.fm/serve/_/8339787/Eterna+Inocencia+Eterna.jpg",
        "uri": "/artists/3",
        "slug": "eterna-inocencia",
        "id": 3
    }


Uniqueness of slugs
~~~~~~~~~~~~~~~~~~~

Slugs are generated from the following fields:

* ``Artist.name``
* ``Album.name``
* ``Track.title``

If the slug clashes with an existing one, then a hyphen and a unique ID will be
appended to it. Due to the possibility of `using slugs instead of IDs`_, if an
slug results in a numeric string a hyphen and a unique ID will be appended to
remove the ambiguity.
