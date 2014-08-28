Meta Resources
==============

Meta resources are simply dynamic or informational resources with no relation
to any database model in particular. They are:

* ``/random/<str:resource_name>``
* ``/whatsnew``
* ``/clients``
* ``/about``


/random
-------

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


/whatsnew
---------

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
