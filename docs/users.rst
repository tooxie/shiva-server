Users
=====

Shiva has a very light user implementation. The idea of users is not to keep a
complex profile of a person, but to serve as an authentication mechanism.

A user consists of:

    * E-mail.
    * Password.
    * An 'is_active' flag.
    * An 'is_admin' flag.
    * A creation date.


User creation
-------------

Issue a ``POST`` request to the ``/users`` resource. Note the the ``GET``
method is disallowed.

.. code:: sh

    curl -d "email=herp@derp.com" http://127.0.0.1:9002/users
