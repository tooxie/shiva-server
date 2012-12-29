=====
Shiva
=====

Dinosaurs will slowly die.


Prerequisites
=============

You are going to need a Last.fm API key. You can get one at
http://www.last.fm/api/account/create

This is used to fetch the artists' images.


Installation
============


* Get the source:

::

    $ git clone https://github.com/tooxie/python-shiva.git
    $ cd python-shiva

* Install dependencies:

::

    $ pip install -r requirements.pip

* Rename shiva/settings/local.py.example to local.py:

::

    $ cp shiva/settings/local.py.example shiva/settings/local.py

* Edit it and configure the directories to scan for music.

  + See `Scanning directories`_ for more info.

* Store your Last.fm API key in *shiva/lastfm.key*:

::

    $ echo "YourLastFMAPIKey" > shiva/lastfm.key

* Add shiva to the PYTHONPATH:

::

  $ export PYTHONPATH=$PYTHONPATH:`pwd`

* Run the indexer:

::

  $ python shiva/indexer.py

* Run the server:

::

  $ python shiva/api.py

* Go to http://127.0.0.1:5000/<resource> (See `Resources`_)


--------------------
Scanning directories
--------------------

To tell Shiva which directories to scan for music, you will have to configure
your `shiva/settings/local.py` file. There you will find a MEDIA_DIRS option
where you need to supply `MediaDir` objects.

This object allows for media configuration. By instantiating a MediaDir class
you can tell Shiva where to look for the media files and how to serve those
files. It's possible to configure the system to look for files on a directory
and serve those files through a different server.

::

    MediaDir(root='/srv/http', dirs=('/music', '/songs),
             url='http://localhost:8080/')

Given that configuration Shiva will scan the directories /srv/http/music and
/srv/http/songs for media files, but they will be served through
http://localhost:8080/music/ and http://localhost:8080/songs/

If just a dir is provided Shiva will serve it through the same instance. This
is *NOT* recommended, but is useful for developing.

::

    MediaDir('/home/fatmike/music')

For more information, check the source of `shiva/media.py`.


Resources
=========

You have the following resources available:

* /artists
* /artist/<int:artist_id>
* /albums
* /album/<int:album_id>
* /tracks
* /track/<int:track_id>
* /lyrics/<int:track_id>


----------------
Artists Resource
----------------


Example request/response:

::

    GET /artist/3
    {
        name: "Eterna Inocencia",
        image: "http://userserve-ak.last.fm/serve/_/8339787/Eterna+Inocencia+Eterna.jpg",
        uri: "/artist/3",
        slug: "eterna-inocencia",
        download_uri: "/artist/3/download",
        id: 3
    }


Fields
------

* download_uri
* id
* image
* name
* slug
* uri


---------------
Albums Resource
---------------

Example request/response:

::

    GET /album/9
    {
        artists: [
            {
                id: 2,
                uri: "/artist/2"
            },
            {
                id: 5,
                uri: "/artist/5"
            }
        ],
        download_uri: "/album/9/download",
        name: "NOFX & Rancid - BYO Split Series (Vol. III)",
        year: 0,
        uri: "/album/9",
        cover: "http://userserve-ak.last.fm/serve/300x300/72986694.jpg",
        id: 9,
        slug: "nofx-rancid-byo-split-series-vol-iii"
    }


Fields
------

* artists
* cover
* download_uri
* id
* name
* slug
* uri
* year


Filtering
---------

The album list accepts an `artist` parameter in which case will filter the list
of albums only to those corresponding to that artist.

Example request/response:

::

    GET /albums/?artist=7
    [
        {
            artists: [
                {
                    id: 7,
                    uri: "/artist/7"
                }
            ],
            download_uri: "/album/12/download",
            name: "Anesthesia",
            year: 2008,
            uri: "/album/12",
            cover: "http://userserve-ak.last.fm/serve/300x300/3489534.jpg",
            id: 12,
            slug: "anesthesia"
        },
        {
            artists: [
                {
                    id: 7,
                    uri: "/artist/7"
                }
            ],
            download_uri: "/album/27/download",
            name: "Kum Kum",
            year: 2008,
            uri: "/album/27",
            cover: "http://userserve-ak.last.fm/serve/300x300/62372889.jpg",
            id: 27,
            slug: "kum-kum"
        }
    ]


--------------
Track Resource
--------------

Example request/response:

::

    GET /track/484
    {
        number: 4,
        download_uri: "/track/484/download",
        path: "/srv/music/nofx-pump_up_the_valuum/04. Dinosaurs Will Die.mp3",
        bitrate: 128,
        slug: "dinosaurs-will-die",
        album: {
            id: 34,
            uri: "/album/34"
        },
        title: "Dinosaurs Will Die",
        uri: "/track/484",
        id: 484,
        length: 180
    }


Fields
------

* album
* bitrate
* download_uri
* id
* length
* number
* path
* slug
* title
* uri


Filtering
---------

The track listing accepts 1 of 2 possible parameters to filter down the list
only to those tracks corresponding to a given `album` or `artist`.


By artist
~~~~~~~~~

Example request/response:

::

    GET /tracks?artist=35
    [
        {
            album: {
                id: 35,
                uri: "/album/35"
            },
            length: 189,
            number: 1,
            title: "Pay Cheque (Heritage II)",
            path: "/srv/music/ftd-2003-sofa_so_good/01 For The Day - Pay Cheque
            (Heritage II).mp3",
            slug: "pay-cheque-heritage-ii",
            download_uri: "/track/497/download",
            bitrate: 196,
            id: 497,
            uri: "/track/497"
        },
        {
            album: {
                id: 35,
                uri: "/album/35"
            },
            length: 171,
            number: 2,
            title: "In Your Dreams",
            path: "/srv/music/ftd-2003-sofa_so_good/02 For The Day - In Your
            Dreams.mp3",
            slug: "in-your-dreams",
            download_uri: "/track/505/download",
            bitrate: 186,
            id: 505,
            uri: "/track/505"
        }
    ]


By album
~~~~~~~~

::

    GET /tracks?album=17
    [
        {
            album: {
                id: 17,
                uri: "/album/17"
            },
            length: 132,
            number: 1,
            title: "Shapes",
            path: "/srv/music/flip-keep_rockin/flip-01-shapes.mp3",
            slug: "shapes",
            download_uri: "/track/263/download",
            bitrate: 192,
            id: 263,
            uri: "/track/263"
        },
        {
            album: {
                id: 17,
                uri: "/album/17"
            },
            length: 118,
            number: 2,
            title: "Stucked to The Ground",
            path: "/srv/music/flip-keep_rockin/flip-02-stucked_to_the_ground.mp3",
            slug: "stucked-to-the-ground",
            download_uri: "/track/267/download",
            bitrate: 192,
            id: 267,
            uri: "/track/267"
        }
    ]


---------------
Lyrics Resource
---------------

Example request/response:

::

    GET /lyrics/268
    {
        track: {
            id: 268,
            uri: "/track/268"
        },
        uri: "http://lyrics.wikia.com/Flip:Wrong_Side",
        lyrics: "Along our way We've got to choose 'tween what's wrong or right Basically our l[...]",
        artist: {
            id: 8,
            uri: "/artist/8"
        }
    }


Have in mind
------------

* Due to legal issues lyric-providers are not allowed to send the complete
  text, but just a small snippet considered "Fair Use".
* Insted, they are forced to send traffic to their website in order
  to track users.

  + For more info read http://api.wikia.com/wiki/LyricWiki_API#FAQs

* For that same reason this software does not store lyrics, but fetches them
  every time. This is inefficient, I know.
* Also, the LyricWiki API is, so to say, quite sensitive and may not find the
  lyrics you request unless the artist is in the correct case.


Assumptions
===========

For the sake of simplicity many assumptions were made that will eventually be
worked on and improved/removed.

* Only music files.

  + Actually, only mp3 files.

* No users.

  + Therefore, no customization.
  + And no privacy.

* No uploading of files.
* No update of ID3 info when DB info changes.


Wish list
=========

* Index your music and videos.

  + Which formats? Ogg? Wav?

* Batch-edit ID3 tags.
* Download your songs in batch.
* Users.
* Share your music with your friends.
* Share your music with your friends' servers.
* Listen to your friends' music.
* They can also upload their music.
* Stream audio and video. (Radio mode)
* Set up a radio and collaboratively pick the music.
* Browse your collection by artist/album.
* Your music, your rules.


Why Shiva?
==========

https://en.wikipedia.org/wiki/Shiva_crater
