=====
Shiva
=====

Something related to música.


Wish list
=========

* Indexes your music and videos.
* Lets you batch-edit your ID3 tags.
* You can listen to your songs.
* You can download your songs by one or in batch.
* Share your music with your friends.
* Share your music with other servers.
* Listen to your friend's music.
* Stream audio and video.
* They can also upload their music.
* Set up a radio and collaboratively pick the music.
* No playlists, pick your songs by artist/album.
* Your music, your rules.
* A better motto.


Installation
============

* Install dependencies:
  $ pip install -r doc/requirements.txt
* Add shiva to the PYTHONPATH.


Usage
=====

* Rename shiva/www/settings/local.py.example to local.py.
* Edit it and configure the directories to scan for music.
* Run the walker:
  $ python walker.py
* Run the server:
  $ python shiva/www/runserver.py
* Go to http://127.0.0.1:5000/ or http://127.0.0.1:5000/admin/
