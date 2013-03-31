# -*- coding: utf-8 -*-
"""Music indexer for the Shiva-Server API.
Index your music collection and (optionally) retrieve album covers and artist
pictures from Last.FM.

Usage:
    shiva-indexer [-h] [-v] [-q] [--lastfm] [--nometadata]

Options:
    -h, --help    Show this help message and exit
    --lastfm      Retrieve artist and album covers from Last.FM API.
    --nometadata  Don't read file's metadata when indexing.
    -v --verbose  Show debugging messages about the progress.
    -q --quiet    Suppress warnings.
"""
# K-Pg
import logging
from datetime import datetime
import os
import sys

from docopt import docopt

from shiva import models as m
from shiva.app import app, db
from shiva.utils import MetadataManager

q = db.session.query


class Indexer(object):
    def __init__(self, config=None, use_lastfm=False, no_metadata=False,
                 verbose=False, quiet=False):
        self.config = config
        self.use_lastfm = use_lastfm
        self.no_metadata = no_metadata
        self.verbose = verbose
        self.quiet = quiet

        self.track_count = 0

        self.session = db.session
        self.media_dirs = config.get('MEDIA_DIRS', [])

        self._meta = None

        self.artists = {}
        self.albums = {}

        if self.use_lastfm:
            import pylast

            self.pylast = pylast
            api_key = config['LASTFM_API_KEY']
            self.lastfm = self.pylast.LastFMNetwork(api_key=api_key)

        if not len(self.media_dirs):
            print("Remember to set the MEDIA_DIRS option, otherwise I don't "
                  'know where to look for.')

    def get_artist(self, name):
        if name in self.artists:
            return self.artists[name]
        else:
            cover = None
            if self.use_lastfm:
                cover = self.lastfm.get_artist(name).get_cover_image()
            artist = m.Artist(name=name, image=cover)
            self.session.add(artist)
            self.artists[name] = artist

        return artist

    def get_album(self, name, artist):
        if name in self.albums:
            return self.albums[name]
        else:
            release_year = self.get_release_year()
            cover = None
            if self.use_lastfm:
                try:
                    _artist = self.lastfm.get_artist(artist.name)
                    _album = self.lastfm.get_album(_artist, name)
                    release_year = self.get_release_year(_album)
                    pylast_cover = self.pylast.COVER_EXTRA_LARGE
                    cover = _album.get_cover_image(size=pylast_cover)
                except self.pylast.WSError, error:
                    #TODO: proper log error
                    print(error)

            album = m.Album(name=name, year=release_year, cover=cover)
            self.session.add(album)
            self.albums[name] = album

        return album

    def get_release_year(self, lastfm_album=None):
        if not self.use_lastfm or not lastfm_album:
            return self.get_metadata_reader().release_year

        _date = lastfm_album.get_release_date()
        if not _date:
            if not self.get_metadata_reader().release_year:
                return None

            return self.get_metadata_reader().release_year

        return datetime.strptime(_date, '%d %b %Y, %H:%M').year

    def save_track(self):
        """
        Takes a path to a track, reads its metadata and stores everything in
        the database.

        """

        full_path = self.file_path.decode('utf-8')

        track = m.Track(full_path)
        if self.no_metadata:
            self.session.add(track)
            if self.verbose:
                print 'Added track without metadata: %s' % full_path
            return
        else:
            if q(m.Track).filter_by(path=full_path).count():
                if self.verbose:
                    print 'Skipped existing track: %s' % full_path
                return

        meta = self.get_metadata_reader()

        artist = self.get_artist(meta.artist)
        album = self.get_album(meta.album, artist)

        if artist is not None and artist not in album.artists:
            album.artists.append(artist)

        track.album = album
        track.artist = artist
        self.session.add(track)

        if self.verbose:
            print 'Added track: %s' % full_path

        self.track_count += 1
        if self.track_count % 10 == 0:
            self.session.commit()
            if self.verbose:
                print 'Writing to database...'

    def get_metadata_reader(self):
        if not self._meta or self._meta.origpath != self.file_path:
            self._meta = MetadataManager(self.file_path)
        return self._meta

    def is_track(self):
        """Try to guess whether the file is a valid track or not."""
        if not os.path.isfile(self.file_path):
            return False

        if '.' not in self.file_path:
            return False

        ext = self.file_path.rsplit('.', 1)[1]
        if ext not in app.config.get('VALID_FILE_EXTENSIONS', []):
            if not self.quiet:
                msg = 'Skipped file with unknown file extension: %s'
                print msg % self.file_path
            return False

        return True

    def walk(self, target):
        """Recursively walks through a directory looking for tracks."""

        # If target is a file, try to save it as a track
        if os.path.isfile(target):
            self.file_path = target
            if self.is_track():
                self.save_track()

        # Otherwise, recursively walk the directory looking for files
        else:
            for root, dirs, files in os.walk(target):
                for name in files:
                    self.file_path = os.path.join(root, name)
                    if self.is_track():
                        self.save_track()

    def run(self):
        for mobject in self.media_dirs:
            for mdir in mobject.get_valid_dirs():
                self.walk(mdir)


def main():
    arguments = docopt(__doc__)

    use_lastfm = arguments['--lastfm']
    no_metadata = arguments['--nometadata']

    if no_metadata:
        use_lastfm = False

    if use_lastfm and not app.config.get('LASTFM_API_KEY'):
        sys.stderr.write('ERROR: You need a Last.FM API key if you set the '
                         '--lastfm flag.\n')
        sys.exit(1)

    lola = Indexer(app.config, use_lastfm=use_lastfm, no_metadata=no_metadata,
                   verbose=arguments['--verbose'], quiet=arguments['--quiet'])
    lola.run()

    # Petit performance hack: Every track will be added to the session but they
    # will be written down to disk only once, at the end.
    lola.session.commit()
