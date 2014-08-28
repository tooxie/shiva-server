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
