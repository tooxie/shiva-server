# -*- coding: utf-8 -*-
"""Music indexer for the Shiva-Server API.
Index your music collection and (optionally) retrieve album covers and artist
pictures from Last.FM.

Usage:
    shiva-indexer [-h] [-f] [-v] [-q] [--lastfm] [--nometadata] [--reindex]
                  [--force] [--verbose-sql]

Options:
    -h, --help     Show this help message and exit
    --lastfm       Retrieve artist and album covers from Last.FM API.
    --nometadata   Don't read file's metadata when indexing.
    --reindex      Remove all existing data from the database before indexing.
    -f, --force    Do not ask any questions. DANGER: This can destroys your
                   database when used with --reindex.
    --verbose-sql  Print every SQL statement. Be careful, it's a little too
                   verbose.
    -v --verbose   Show debugging messages about the progress.
    -q --quiet     Suppress warnings.
"""
# K-Pg
from datetime import datetime
from multiprocessing.pool import Pool
from time import time
import logging
import itertools
import sys
import traceback

from docopt import docopt
from sqlalchemy import func

from shiva import models as m
from shiva.app import app, db
from shiva.exceptions import MetadataManagerReadError
from shiva.utils import ignored, get_logger

q = db.session.query
log = get_logger()


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

allowed_extensions = app.config.get('ALLOWED_FILE_EXTENSIONS',
                                    VALID_FILE_EXTENSIONS)

albums = {}
artists = {}
skipped_tracks = 0


def is_track(path):
    if '.' not in path:
        return False

    ext = path.rsplit('.', 1)[1].lower()
    if ext not in VALID_FILE_EXTENSIONS:
        log.debug('[ SKIPPED ] %s (Unrecognized extension)' % path)
        return False

    if ext not in allowed_extensions:
        log.debug('[ SKIPPED ] %s (Ignored extension)' % path)
        return False

    return True


def skip(path, reason=None, print_traceback=None):
    global skipped_tracks
    skipped_tracks += 1

    if log.getEffectiveLevel() <= logging.INFO:
        _reason = ' (%s)' % reason if reason else ''
        log.info('[ SKIPPED ] %s%s' % (path, _reason))

        if print_traceback:
            log.info(traceback.format_exc())

    return True


def add_to_session(track):
    db.session.add(track)
    log.info('[ OK ] %s' % track.path)


def get_lastfm():
    import pylast

    api_key = app.config['LASTFM_API_KEY']
    return pylast.LastFMNetwork(api_key=api_key)


def get_artist(name, use_lastfm=False):
    # TODO use_lastfm
    global artists

    name = name.strip() if (type(name) in (str, unicode)) else None
    if not name:
        return None

    if name in artists:
        return artists[name]
    else:
        cover = None
        if use_lastfm:
            log.debug('[ Last.FM ] Retrieving "%s" info' % name)
            with ignored(Exception, print_traceback=True):
                lastfm = get_lastfm()
                cover = lastfm.get_artist(name).get_cover_image()
        artist = m.Artist(name=name, image=cover)
        db.session.add(artist)
        artists[name] = artist

    return artist


def get_release_year(track, lastfm_album=None):
    if not lastfm_album:
        return track.get_metadata_reader().release_year

    _date = lastfm_album.get_release_date()
    if not _date:
        if not track.get_metadata_reader().release_year:
            return None

        return track.get_metadata_reader().release_year

    return datetime.strptime(_date, '%d %b %Y, %H:%M').year


def get_album(track, artist, use_lastfm=False):
    global albums
    name = track.album.strip() if type(track.album) in (str,
                                                        unicode) else None
    if not name or not artist:
        return None

    if name in albums:
        return albums[name]
    else:
        release_year = get_release_year()
        cover = None

        album = m.Album(name=name, year=release_year, cover=cover)
        db.session.add(album)
        albums[name] = album

    return album


def save_track(path, empty_db=False, no_metadata=False):
    try:
        full_path = path.decode('utf-8')
    except UnicodeDecodeError:
        skip('Unrecognized encoding', print_traceback=True)

        # If file name is in an strange encoding ignore it.
        return False

    try:
        track = m.Track(full_path, no_metadata=no_metadata)
    except MetadataManagerReadError:
        skip('Corrupted file', print_traceback=True)

        # If the metadata manager can't read the file, it's probably not an
        # actual music file, or it's corrupted. Ignore it.
        return False

    if not empty_db:
        # TODO: can be made a lot faster by pre-fetching known paths
        if q(m.Track).filter_by(path=full_path).count():
            skip(full_path)

            return True

    if no_metadata:
        add_to_session(track)

        return True

    meta = track.get_metadata_reader()

    artist = get_artist(meta.artist)
    album = get_album(track, artist)

    if artist is not None and album is not None:
        if artist not in album.artists:
            album.artists.append(artist)

    track.album = album
    track.artist = artist
    add_to_session(track)
    return True


def get_paths():
    media_dirs = app.config.get('MEDIA_DIRS', None)
    if media_dirs is None:
        log.error("Remember to set the MEDIA_DIRS option, otherwise I "
                  "don't know where to look for.")
        raise
    list_of_path_lists = [x.get_paths() for x in media_dirs]
    flat_paths = itertools.chain.from_iterable(list_of_path_lists)
    return flat_paths


def run():
    initial_time = time()
    paths = get_paths()
    valid_paths = [x for x in paths if is_track(x)]
    pool = Pool(processes=4)
    # map_result example: [True, True, False, True]
    # means: 3 tracks ok, 1 track skipped
    map_result = pool.map(save_track, valid_paths)
    count_ok = len([1 for x in map_result if x is True])
    count_skipped = len([x for x in map_result if x is False])
    final_time = time()
    return count_ok, count_skipped, initial_time, final_time


def print_stats(track_count, skipped_tracks, initial_time, final_time):
    if track_count == 0:
        log.info('\nNo track indexed.\n')

        return True

    elapsed_time = final_time - initial_time
    log.info('\nRun in %d seconds. Avg %.3fs/track.' % (
        elapsed_time,
        (elapsed_time / track_count)))
    log.info('Found %d tracks. Skipped: %d. Indexed: %d.' % (
        track_count,
        skipped_tracks,
        (track_count - skipped_tracks)))
    # TODO: enable count by extension
    # for extension, count in self.count_by_extension.iteritems():
    #     if count:
    #         log.info('%s: %d tracks' % (extension, count))


def _make_unique(model):
    """
    Retrieves all repeated slugs for a given model and appends the
    instance's primary key to it.

    """

    slugs = q(model).group_by(model.slug). \
        having(func.count(model.slug) > 1)

    for row in slugs:
        for instance in q(model).filter_by(slug=row.slug):
            instance.slug += '-%s' % instance.pk

    return slugs


def make_slugs_unique():
    query = _make_unique(m.Artist)
    db.session.add_all(query)

    query = _make_unique(m.Track)
    db.session.add_all(query)

    db.session.commit()


def main():
    arguments = docopt(__doc__)

    if arguments['--reindex']:
        if not arguments['--force']:
            confirmed = raw_input('This will destroy all the information. '
                                  'Proceed? [y/N] ') in ('y', 'Y')
            if not confirmed:
                log.error('Aborting.')
                sys.exit(1)

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

    count, skipped, t0, t1 = run()
    print_stats(count, skipped, t0, t1)

    # Petit performance hack: Every track will be added to the session but they
    # will be written down to disk only once, at the end.
    log.debug('Writing to database...')
    db.session.commit()

    log.debug('Checking for duplicated tracks...')
    make_slugs_unique()


if __name__ == '__main__':
    main()
