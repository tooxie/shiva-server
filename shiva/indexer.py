# -*- coding: utf-8 -*-
"""Music indexer for the Shiva-Server API.
Index your music collection and (optionally) retrieve album covers and artist
pictures from Last.FM.

Usage:
    shiva-indexer [-h] [-v] [-q] [--lastfm] [--nometadata] [--reindex]

Options:
    -h, --help    Show this help message and exit
    --lastfm      Retrieve artist and album covers from Last.FM API.
    --nometadata  Don't read file's metadata when indexing.
    --reindex     Remove all existing data from the database before indexing.
    -v --verbose  Show debugging messages about the progress.
    -q --quiet    Suppress warnings.
"""
# K-Pg
from datetime import datetime
from slugify import slugify
import logging
import os
import sys

from docopt import docopt
from sqlalchemy import func

from shiva import models as m
from shiva.app import app, db
from shiva.utils import ignored

q = db.session.query


class Indexer(object):

    VALID_FILE_EXTENSIONS = (
        'asf', 'wma',  # ASF
        'flac',  # FLAC
        'mp4', 'm4a', 'm4b', 'm4p',  # M4A
        'ape',  # Monkey's Audio
        'mp3',  # MP3
        'mpc', 'mp+', 'mpp',  # Musepack
        'spx',  # Ogg Speex
        'ogg', 'oga',  # Ogg Vorbis / Theora
        'tta',  # True Audio
        'wv',  # WavPack
        'ofr',  # OptimFROG
    )

    def __init__(self, config=None, use_lastfm=False, no_metadata=False,
                 reindex=False, verbose=False, quiet=False):
        self.config = config
        self.use_lastfm = use_lastfm
        self.no_metadata = no_metadata
        self.verbose = verbose
        self.quiet = quiet

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

        if reindex:
            if not self.quiet:
                print('Dropping database...')

            confirmed = raw_input('This will destroy all the information. '
                                  'Proceed? [y/N] ') in ('y', 'Y')
            if not confirmed:
                print('Aborting.')
                sys.exit(1)

            db.drop_all()

            if not self.quiet:
                print('Recreating database...')
            db.create_all()

    def get_artist(self, name):
        _name = slugify(name)
        if _name in self.artists:
            return self.artists[_name]
        else:
            cover = None
            if self.use_lastfm:
                with ignored(Exception, print_traceback=True):
                    cover = self.lastfm.get_artist(name).get_cover_image()
            artist = m.Artist(name=name, image=cover)
            self.session.add(artist)
            self.artists[_name] = artist

        return artist

    def get_album(self, name, artist):
        _name = slugify(name)
        if _name in self.albums:
            return self.albums[_name]
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
            self.albums[_name] = album

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
        self.set_metadata_reader(track)
        if self.no_metadata:
            self.session.add(track)
            if not self.quiet:
                print('[ OK ] %s' % full_path)

            return True
        else:
            if q(m.Track).filter_by(path=full_path).count():
                if not self.quiet:
                    print('[ SKIPPED ] %s' % full_path)

                return True

        meta = self.get_metadata_reader()

        artist = self.get_artist(meta.artist)
        album = self.get_album(meta.album, artist)

        if artist is not None and artist not in album.artists:
            album.artists.append(artist)

        track.album = album
        track.artist = artist
        self.session.add(track)

        if not self.quiet:
            print('[ OK ] %s' % full_path)

    def get_metadata_reader(self):
        return self._meta

    def set_metadata_reader(self, track):
        self._meta = track.get_metadata_reader()

    def is_track(self):
        """Try to guess whether the file is a valid track or not."""
        if not os.path.isfile(self.file_path):
            return False

        if '.' not in self.file_path:
            return False

        ext = self.file_path.rsplit('.', 1)[1]
        if ext not in self.VALID_FILE_EXTENSIONS:
            if self.verbose:
                msg = 'Skipped file with unknown file extension: %s'
                print(msg % self.file_path)

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

    # SELECT pk, slug, COUNT(*) FROM tracks GROUP BY slug HAVING COUNT(*) > 1;
    def make_slugs_unique(self):
        """
        Retrieves all repeated slugs and appends the instance's primary key to
        it.

        """

        query = q(m.Track).group_by(m.Track.slug).\
            having(func.count(m.Track.slug) > 1)

        for _track in query:
            slug = _track.slug
            for track in q(m.Track).filter_by(slug=slug):
                track.slug += '-%s' % track.pk
                self.session.add(track)

        self.session.commit()

    def run(self):
        for mobject in self.media_dirs:
            for mdir in mobject.get_valid_dirs():
                self.walk(mdir)


def main():
    arguments = docopt(__doc__)

    kwargs = {
        'use_lastfm': arguments['--lastfm'],
        'no_metadata': arguments['--nometadata'],
        'reindex': arguments['--reindex'],
        'verbose': arguments['--verbose'],
        'quiet': arguments['--quiet'],
    }

    if kwargs['no_metadata']:
        kwargs['use_lastfm'] = False

    if kwargs['use_lastfm'] and not app.config.get('LASTFM_API_KEY'):
        sys.stderr.write('ERROR: You need a Last.FM API key if you set the '
                         '--lastfm flag.\n')
        sys.exit(1)

    # Generate database
    db.create_all()

    lola = Indexer(app.config, **kwargs)
    lola.run()

    # Petit performance hack: Every track will be added to the session but they
    # will be written down to disk only once, at the end.
    if lola.verbose:
        print('Writing to database...')
    lola.session.commit()

    if lola.verbose:
        print('Checking for duplicated tracks...')
    lola.make_slugs_unique()


if __name__ == '__main__':
    main()
