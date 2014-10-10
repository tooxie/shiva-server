Users
=====

Shiva has a very light user implementation. The idea of users is not to keep a
complex profile of a person, but to serve as an authentication mechanism.

A user consists of:

    * E-mail.
    * Password.
    * An 'is_public' flag.
    * An 'is_active' flag.
    * An 'is_admin' flag.
    * A creation date.


User creation
-------------

Issue a ``POST`` request to the ``/users`` resource. Note the the ``GET``
method will only list those users whose ``is_public`` attribute is set to
``True``.

.. code:: sh

    curl -d "email=herp@derp.com" http://127.0.0.1:9002/users


Authentication
--------------

Authentication is done against the ``/users/login`` endpoint. You will receive
a token that, if the ``ALLOW_ANONYMOUS_ACCESS`` setting is set to ``False``
(which by default it is), has to be included with every request for as long as
it's valid. Once it is no longer valid you will get a ``401 Unauthorized`` and
will have to re-authenticate.

.. code:: sh

    curl -d "email=herp@derp.com" -d "password=s3cr37" http://127.0.0.1:9002/users/login

It will return something like:

.. code:: javascript

    {
        "token": "eyJhbGciOiJIUzI1NiIsImV4cCI6MTQxMTUwNDczMywiaWF0IjoxNDExNTAzMjkzfQ.eyJwayI6MX0.7vNzVWGr-gJX7qygFJKM5x6dCVZapKTSsI2IzwYggLY"
    }

You then need to include that token with your every request:

.. code:: sh

    curl http://127.0.0.1:9002/tracks?token=$AUTH_TOKEN


Role-based Access Control
=========================

The concept of Roles is very limited in Shiva. There are 3 possible roles:

* User
* Admin
* Shiva

The first 2 are assigned to users, the last one is only used by other Shiva
instances to communicate with each other. Please note that this functionality 
is not yet implemented.

To create a normal user (i.e. either *User* or *Admin* roles) use the command
`shiva-admin user add`.

A role-authentication failure will result in a 401 Forbidden status code.
