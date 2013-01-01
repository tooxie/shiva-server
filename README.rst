=====
Shiva
=====

Dinosaurs will slowly die.


What is Shiva?
==============

* An API to your music.
* A music player.
* A music collection organizer.


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

* Rename shiva/api/settings/local.py.example to local.py:

::

    $ cp shiva/api/settings/local.py.example shiva/api/settings/local.py

* Edit it and configure the directories to scan for music.

  + See `Scanning directories`_ for more info.

* Set the LASTFM_API_KEY setting with the key you got from Last.fm.
* Configure your LOCATION (`See available choices <http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE>`__)
* Add shiva to the PYTHONPATH:

::

  $ export PYTHONPATH=$PYTHONPATH:`pwd`

* Run the indexer:

::

  $ python shiva/indexer.py

* Run the server:

::

  $ python shiva/api/app.py

* Go to http://127.0.0.1:5000/<resource> (See `Resources`_)


--------------------
Scanning directories
--------------------

To tell Shiva which directories to scan for music, you will have to configure
your `shiva/app/config/local.py` file. There you will find a MEDIA_DIRS option
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
* /artist/<int:artist_id>/shows
* /albums
* /album/<int:album_id>
* /tracks
* /track/<int:track_id>
* /track/<int:track_id>/lyrics


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

* download_uri: The URI to download this artist's tracks. (NOT IMPLEMENTED)
* id: The object's ID.
* image: Link to a photo. (Provided by last.fm)
* name: Artist's name.
* slug: A `slug <https://en.wikipedia.org/wiki/Slug_(web_publishing)#Slug>`__
  of the artist's name.
* uri: The URI of this resource's instance.


--------------
Shows Resource
--------------

Returns a structure provided by BandsInTown.com as is.

Example request/response:

::

    GET /artist/1/shows
    [
        {
            "artists": [
                {
                    "image_url": "http://www.bandsintown.com/Lagwagon/photo/medium.jpg",
                    "name": "Lagwagon",
                    "mbid": "c7788fba-e635-4d8b-a937-01a68ab154e3",
                    "facebook_tour_dates_url": "http://bnds.in/HE8iWo",
                    "thumb_url": "http://www.bandsintown.com/Lagwagon/photo/small.jpg"
                }
            ],
            "formatted_datetime": "Friday, January 18, 2013 at 7:00pm",
            "ticket_type": "Tickets",
            "formatted_location": "Hollywood, CA",
            "title": "Lagwagon @ Hollywood Palladium in Hollywood, CA",
            "facebook_share_url": "<annoyingly long fb url>",
            "ticket_status": "available",
            "id": "5869403",
            "description": null,
            "venue": {
                "city": "Hollywood",
                "name": "Hollywood Palladium",
                "latitude": "34.0981410",
                "region": "CA",
                "country": "United States",
                "longitude": "-118.3242730"
            },
            "facebook_rsvp_url": "http://www.bandsintown.com/event/5869403/facebook_rsvp?app_id=MY_APP_ID&artist=Lagwagon&came_from=67",
            "on_sale_datetime": "2012-11-02T10:00:00",
            "datetime": "2013-01-18T19:00:00",
            "ticket_url": "http://www.bandsintown.com/event/5869403/buy_tickets?app_id=MY_APP_ID&artist=Lagwagon"
        }
    ]


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
        year: 2002,
        uri: "/album/9",
        cover: "http://userserve-ak.last.fm/serve/300x300/72986694.jpg",
        id: 9,
        slug: "nofx-rancid-byo-split-series-vol-iii"
    }


Fields
------

* artists: A list of the artists involved in that record.
* cover: A link to an image of the album's cover. (Provided by last.fm)
* download_uri: The URI to download this album. (NOT IMPLEMENTED)
* id: The object's ID.
* name: The album's name.
* slug: A `slug <https://en.wikipedia.org/wiki/Slug_(web_publishing)#Slug>`__
  of the album's name.
* uri: The URI of this resource's instance.
* year: The release year of the album.


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
            year: 1995,
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
            year: 1996,
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

* album: The album to which this track belongs.
* bitrate: In MP3s this value is directly proportional to the
  `sound quality <https://en.wikipedia.org/wiki/Bit_rate#MP3>`__.
* download_uri: The URI to download this track.
* id: The object's ID.
* length: The length in seconds of the track.
* number: The `ordinal number <https://en.wikipedia.org/wiki/Ordinal_number>`__
  of this track with respect to this album.
* slug: A `slug <https://en.wikipedia.org/wiki/Slug_(web_publishing)#Slug>`__
  of the track's title.
* title: The title of the track.
* uri: The URI of this resource's instance.


Filtering
---------

The track listing accepts 1 of 2 possible parameters to filter down the list
only to those tracks corresponding to a given `album` or `artist`.


By artist
~~~~~~~~~

Example request/response:

::

    GET /tracks?artist=16
    [
        {
            album: {
                id: 36,
                uri: "/album/36"
            },
            length: 189,
            artist: {
                id: 16,
                uri: "/artist/16"
            },
            number: 1,
            title: "Pay Cheque (Heritage II)",
            slug: "pay-cheque-heritage-ii",
            download_uri: "/track/523/download",
            bitrate: 196,
            id: 523,
            uri: "/track/523"
        },
        {
            album: {
                id: 36,
                uri: "/album/36"
            },
            length: 171,
            artist: {
                id: 16,
                uri: "/artist/16"
            },
            number: 2,
            title: "In Your Dreams",
            slug: "in-your-dreams",
            download_uri: "/track/531/download",
            bitrate: 186,
            id: 531,
            uri: "/track/531"
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

    GET /track/268/lyrics
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


Keep in mind
------------

* Due to legal issues lyric-providers are not allowed to send the complete
  text, but just a small snippet considered "Fair Use".
* Instead, they are forced to send traffic to their website in order to track
  users.

  + For more info read http://api.wikia.com/wiki/LyricWiki_API#FAQs

* For that same reason this software does not store lyrics, but fetches them
  every time. This is inefficient, I know.
* Also, the LyricWiki API is, so to say, quite sensitive and may not find the
  lyrics you request unless the artist is in the correct case.


Assumptions
===========

For the sake of simplicity many assumptions were made that will eventually be
worked on and improved/removed.

* Only music files. No videos.

  + Actually, only mp3 files.

* No users.

  + Therefore, no customization.
  + And no privacy (You can still use
    `htpasswd <https://httpd.apache.org/docs/2.2/programs/htpasswd.html>`__,
    thou.)

* No uploading of files.
* No update of ID3 info when DB info changes.


Known issues
============

* The ID3 reader doesn't always detect the bit rate correctly. Seems like a
  common issue to many libraries, at least the ones I tried.
* The lyrics API may not find the lyrics unless the artist is in the correct
  case.


Wish list
=========

* Index your music and videos.

  + Which formats? Ogg? Wav?

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
* Better lyrics engine.
* Tabs.


Why Shiva?
==========

https://en.wikipedia.org/wiki/Shiva_crater
