# -*- coding: utf-8 -*-
"""Music indexer for the Shiva-Server API.
Index your music collection and (optionally) retrieve album covers and artist
pictures from Last.FM.

Usage:
    shiva-indexer [-h] [-v] [-q] [--lastfm] [--nometadata] [--low-ram]
                  [--reindex] [--verbose-sql]

Options:
    -h, --help     Show this help message and exit
    --lastfm       Retrieve artist and album covers from Last.FM API.
    --nometadata   Don't read file's metadata when indexing.
    --low-ram      Keep RAM usage as low as possible.
    --reindex      Remove all existing data from the database before indexing.
    --verbose-sql  Print every SQL statement. Be careful, it's a little too
                   verbose.
    -v --verbose   Show debugging messages about the progress.
    -q --quiet     Suppress warnings.
"""
# K-Pg
from datetime import datetime
from time import time
import logging
import os
import sys
import traceback

from docopt import docopt
from sqlalchemy import func
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm.exc import NoResultFound

from shiva import models as m
from shiva.app import app, db
from shiva.exceptions import MetadataManagerReadError
from shiva.utils import ignored, get_logger

q = db.session.query
log = get_logger()


class CacheManager(object):
    """
    Class that handles object caching and retrieval. The indexer should not
    access DB directly, it should instead ask for the objects to this class.

    """

    def __init__(self, ram_cache=True, use_db=True):
        log.debug('[CACHE] Initilizing...')

        if not ram_cache:
            log.debug('[CACHE] Ignoring RAM cache')
        self.ram_cache = ram_cache
        self.use_db = use_db

        self.artists = {}
        self.albums = {}

    def get_artist(self, name):
        artist = self.artists.get(name)

        if not artist:
            if self.use_db:
                try:
                    artist = q(m.Artist).filter_by(name=name).one()
                except NoResultFound:
                    pass
                if artist and self.ram_cache:
                    self.add_artist(artist)

        return artist

    def add_artist(self, artist):
        if self.ram_cache:
            self.artists[artist.name] = artist

    def get_album(self, name, artist):
        album = self.albums.get(artist.name, {}).get(name)

        if not album:
            if self.use_db:
                try:
                    album = q(m.Album).filter_by(name=name).one()
                except NoResultFound:
                    pass
                if album and self.ram_cache:
                    self.add_album(album, artist)

        return album

    def add_album(self, album, artist):
        if self.ram_cache:
            if not self.albums.get(artist.name):
                self.albums[artist.name] = {}

            self.albums[artist.name][album.name] = album

    def clear(self):
        self.artists = {}
        self.albums = {}


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
                 low_ram=False, reindex=False):
        self.config = config
        self.use_lastfm = use_lastfm
        self.no_metadata = no_metadata
        self.low_ram = low_ram
        self.reindex = reindex
        self.empty_db = reindex and not low_ram

        self.session = db.session
        self.media_dirs = config.get('MEDIA_DIRS', [])
        self.allowed_extensions = app.config.get('ALLOWED_FILE_EXTENSIONS',
                                                 self.VALID_FILE_EXTENSIONS)

        self._ext = None
        self._meta = None
        self.track_count = 0
        self.skipped_tracks = 0
        self.count_by_extension = {}
        for extension in self.allowed_extensions:
            self.count_by_extension[extension] = 0

        self.artists = {}
        self.albums = {}

        if self.use_lastfm:
            import pylast

            self.pylast = pylast
            api_key = config['LASTFM_API_KEY']
            self.lastfm = self.pylast.LastFMNetwork(api_key=api_key)

        if not len(self.media_dirs):
            log.error("Remember to set the MEDIA_DIRS option, otherwise I "
                      "don't know where to look for.")

        if reindex:
            log.info('Dropping database...')

            confirmed = raw_input('This will destroy all the information. '
                                  'Proceed? [y/N] ') in ('y', 'Y')
            if not confirmed:
                log.error('Aborting.')
                sys.exit(1)

            db.drop_all()

            log.info('Recreating database...')
            db.create_all()

        # This is useful to know if the DB is empty, and avoid some checks
        if not self.reindex and not self.low_ram:
            try:
                m.Artist.query.limit(1).all()
            except OperationalError:
                self.empty_db = True

    def get_artist(self, name):
        name = name.strip() if type(name) in (str, unicode) else None
        if not name:
            return None

        if name in self.artists:
            return self.artists[name]
        else:
            cover = None
            if self.use_lastfm:
                log.debug('[ Last.FM ] Retrieving "%s" info' % name)
                with ignored(Exception, print_traceback=True):
                    cover = self.lastfm.get_artist(name).get_cover_image()
            artist = m.Artist(name=name, image=cover)
            self.session.add(artist)

            if not self.low_ram:
                self.artists[name] = artist

        return artist

    def get_album(self, name, artist):
        name = name.strip() if type(name) in (str, unicode) else None
        if not name or not artist:
            return None

        if name in self.albums:
            return self.albums[name]
        else:
            release_year = self.get_release_year()
            cover = None
            if self.use_lastfm:
                log.debug('[ Last.FM ] Retrieving album "%s" by "%s"' % (
                          name, artist.name))
                with ignored(Exception, print_traceback=True):
                    _artist = self.lastfm.get_artist(artist.name)
                    _album = self.lastfm.get_album(_artist, name)
                    release_year = self.get_release_year(_album)
                    pylast_cover = self.pylast.COVER_EXTRA_LARGE
                    cover = _album.get_cover_image(size=pylast_cover)

            album = m.Album(name=name, year=release_year, cover=cover)
            self.session.add(album)

            if not self.low_ram:
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

    def add_to_session(self, track):
        self.session.add(track)
        ext = self.get_extension()
        self.count_by_extension[ext] += 1

        log.info('[ OK ] %s' % track.path)

        return True

    def skip(self, reason=None, print_traceback=None):
        self.skipped_tracks += 1

        if log.getEffectiveLevel() <= logging.INFO:
            _reason = ' (%s)' % reason if reason else ''
            log.info('[ SKIPPED ] %s%s' % (self.file_path, _reason))
            if print_traceback:
                log.info(traceback.format_exc())

        return True

    def save_track(self):
        """
        Takes a path to a track, reads its metadata and stores everything in
        the database.

        """

        try:
            full_path = self.file_path.decode('utf-8')
        except UnicodeDecodeError:
            self.skip('Unrecognized encoding', print_traceback=True)

            # If file name is in an strange encoding ignore it.
            return False

        try:
            track = m.Track(full_path, no_metadata=self.no_metadata)
        except MetadataManagerReadError:
            self.skip('Corrupted file', print_traceback=True)

            # If the metadata manager can't read the file, it's probably not an
            # actual music file, or it's corrupted. Ignore it.
            return False

        if not self.empty_db:
            if q(m.Track).filter_by(path=full_path).count():
                self.skip()

                return True

        if self.no_metadata:
            self.add_to_session(track)

            return True

        meta = self.set_metadata_reader(track)

        artist = self.get_artist(meta.artist)
        album = self.get_album(meta.album, artist)

        if artist is not None and album is not None:
            if artist not in album.artists:
                album.artists.append(artist)

        track.album = album
        track.artist = artist
        self.add_to_session(track)

        if self.low_ram:
            self.session.commit()

    def get_metadata_reader(self):
        return self._meta

    def set_metadata_reader(self, track):
        self._meta = track.get_metadata_reader()

        return self._meta

    def get_extension(self):
        return self.file_path.rsplit('.', 1)[1].lower()

    def is_track(self):
        """Try to guess whether the file is a valid track or not."""
        if not os.path.isfile(self.file_path):
            return False

        if '.' not in self.file_path:
            return False

        ext = self.get_extension()
        if ext not in self.VALID_FILE_EXTENSIONS:
            log.debug('[ SKIPPED ] %s (Unrecognized extension)' %
                      self.file_path)

            return False
        elif ext not in self.allowed_extensions:
            log.debug('[ SKIPPED ] %s (Ignored extension)' % self.file_path)

            return False

        return True

    def walk(self, target, exclude=tuple()):
        """Recursively walks through a directory looking for tracks."""

        if not os.path.isdir(target):
            return False

        for root, dirs, files in os.walk(target, exclude):
            for name in files:
                self.file_path = os.path.join(root, name)
                if root in exclude:
                    log.debug('[ EXCLUDED ] %s' % self.file_path)
                else:
                    if self.is_track():
                        self.track_count += 1
                        self.save_track()

    def _make_unique(self, model):
        """
        Retrieves all repeated slugs for a given model and appends the
        instance's primary key to it.

        """

        slugs = q(model).group_by(model.slug).\
            having(func.count(model.slug) > 1)

        for row in slugs:
            slug = row.slug
            for instance in q(model).filter_by(slug=row.slug):
                instance.slug += '-%s' % instance.pk

        return slugs

    # SELECT pk, slug, COUNT(*) FROM tracks GROUP BY slug HAVING COUNT(*) > 1;
    def make_slugs_unique(self):
        query = self._make_unique(m.Artist)
        self.session.add_all(query)

        query = self._make_unique(m.Track)
        self.session.add_all(query)

        self.session.commit()

    def print_stats(self):
        if self.track_count == 0:
            log.info('\nNo track indexed.\n')

            return True

        elapsed_time = self.final_time - self.initial_time
        log.info('\nRun in %d seconds. Avg %.3fs/track.' % (
                 elapsed_time,
                 (elapsed_time / self.track_count)))
        log.info('Found %d tracks. Skipped: %d. Indexed: %d.' % (
                 self.track_count,
                 self.skipped_tracks,
                 (self.track_count - self.skipped_tracks)))
        for extension, count in self.count_by_extension.iteritems():
            if count:
                log.info('%s: %d tracks' % (extension, count))

    def run(self):
        self.initial_time = time()

        for mobject in self.media_dirs:
            for mdir in mobject.get_valid_dirs():
                self.walk(mdir, exclude=mobject.get_excluded_dirs())

        self.final_time = time()


def main():
    arguments = docopt(__doc__)

    if arguments['--quiet']:
        log.setLevel(logging.ERROR)
    elif arguments['--verbose']:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

    if arguments['--verbose-sql']:
        app.config['SQLALCHEMY_ECHO'] = True

    kwargs = {
        'use_lastfm': arguments['--lastfm'],
        'no_metadata': arguments['--nometadata'],
        'low_ram': arguments['--low-ram'],
        'reindex': arguments['--reindex'],
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

    lola.print_stats()

    # Petit performance hack: Every track will be added to the session but they
    # will be written down to disk only once, at the end. Unless the --low-ram
    # flag is set, then every track is immediately persisted.
    log.debug('Writing to database...')
    lola.session.commit()

    log.debug('Checking for duplicated tracks...')
    lola.make_slugs_unique()


if __name__ == '__main__':
    main()
