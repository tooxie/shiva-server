Playlists
=========

Playlists are a way of logically grouping tracks by arbitrary conditions
defined by the user.


/playlists
----------

Example response for the request ``GET /playlists/1``:

.. code:: javascript

    {
        "creation_date": "Mon, 29 Sep 2014 22:28:29 -0000",
        "id": 1,
        "length": 4,
        "name": "Classic essentials",
        "read_only": true,
        "tracks": [
            {
                "id": 3,
                "index": 0,
                "uri": "/tracks/3"
            },
            {
                "id": 1,
                "index": 1,
                "uri": "/tracks/1"
            },
            {
                "id": 2,
                "index": 2,
                "uri": "/tracks/2"
            },
            {
                "id": 4,
                "index": 3,
                "uri": "/tracks/4"
            }
        ],
        "user": {
            "id": 1,
            "uri": "/users/1"
        }
    }


Fields
~~~~~~

* ``id``: The object's ID.
* ``creation_date``: The time the playlist was created.
* ``length``: The tracks count.
* ``name``: The playlist's name.
* ``read_only``: When set to True (the default) only the creator of the
  playlist can add/remove tracks to it.
* ``tracks``: The list of tracks contained by the playlist.
* ``tracks.index``: The track's (0-based) position in the playlist.
* ``user``: The creator of the playlist.


Filtering
~~~~~~~~~

It's possible to get only the playlists for a certain user by using the
``user`` query parameter: ``/playlists?user=1``


Adding tracks
-------------

To add a track to a playlist you have to issue a ``POST`` request to
``/playlists/<id>/add`` with the parameters ``track``, which is a track id, and
``index``, which is the 0-based position the track should occuppy in the
playlist. Example:

.. code: sh

    curl -d "track=4" -d "index=0" "http://127.0.0.1:9002/playlists/1/add"

If the ``index`` value is largen than the number of items in the playlist, a
``400 Bad Request`` will be returned. If the playlist is empty, send
``index=0``. If all went ok, you will get a ``204 No Content`` status code.


Removing tracks
---------------

The procedure for removing tracks is very similar to the addition, the main
difference is that the request is issued against the ``/playlist/<id>/remove``
endpoint:

.. code: sh

    curl -d "index=0" "http://127.0.0.1:9002/playlists/1/remove"

You don't have to include the track id in this case, only the ``index`` is
enough. Just like the addition, if the value of ``index`` is greater than the
number of tracks in the playlist, you will get a ``400 Bad Request``. If all
went ok, a ``204 No Content`` will be returned.
