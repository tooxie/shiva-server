.. |buildstatus| image:: https://secure.travis-ci.org/tooxie/shiva-server.png?branch=master
    :alt: Build status
    :target: http://travis-ci.org/tooxie/shiva-server
.. |testcoverage| image:: https://coveralls.io/repos/tooxie/shiva-server/badge.png
    :alt: Test coverage
    :target: https://coveralls.io/r/tooxie/shiva-server
.. |documentation| image:: https://readthedocs.org/projects/shiva/badge/?version=latest
    :alt: Documentation
    :target: http://shiva.readthedocs.org/en/latest/


=====
Shiva
=====

Dinosaurs will slowly die.

|buildstatus| |testcoverage| |documentation|


License
=======

Please read the LICENSE file distributed with this software.


What is Shiva?
==============

The Mozilla Hacks blog kindly published a nice article that explains the ideas
that inspire this software:
`Shiva: More than a RESTful API to your music collection
<https://hacks.mozilla.org/2013/03/shiva-more-than-a-restful-api-to-your-music-collection/>`_

You can find the technical documentation at `Read The Docs
<http://shiva.readthedocs.org/en/latest/>`_.


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
