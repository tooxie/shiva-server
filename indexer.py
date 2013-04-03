# -*- coding: utf-8 -*-
# K-Pg
import logging
from datetime import datetime
import os
import sys

from shiva import models as m
from shiva.app import app, db
from shiva.utils import ID3Manager

q = db.session.query

USAGE = """Usage: %s [-h] [--lastfm] [--nometadata] [-v] [--verbose]

Music indexer for the Shiva-Server API.

Index your music collection and (optionally) retrieve album covers and artist
pictures from Last.FM.

optional arguments:
    -h, --help    Show this help message and exit
    --lastfm      Retrieve artist and album covers from Last.FM API.
    --nometadata  Don't read file's metadata when indexing.
    -v, --verbose Show debugging messages about the progress.
""" % sys.argv[0]

if '--help' in sys.argv or '-h' in sys.argv:
    print(USAGE)
    sys.exit(0)


class Indexer(object):
    def __init__(self, config=None, use_lastfm=False, no_metadata=False,
                 verbose=False):
        self.config = config
        self.use_lastfm = use_lastfm
        self.no_metadata = no_metadata
        self.verbose = verbose

        self.count = 0
        self.file_count = 0
        self.track_count = 0

        self.session = db.session
        self.media_dirs = config.get('MEDIA_DIRS', [])
        self.id3r = None
        self.artists = {}
        self.albums = {}

        if self.use_lastfm:
            import pylast

            self.pylast = pylast
            api_key = config['LASTFM_API_KEY']
            self.lastfm = self.pylast.LastFMNetwork(api_key=api_key)

        if len(self.media_dirs) == 0:
            print("Remember to set the MEDIA_DIRS option, otherwise I don't "
                  'know where to look for.')

        if len(config.get('ACCEPTED_FORMATS', [])) == 0:
            print("Remember to set the ACCEPTED_FORMATS option, "
                  "otherwise I don't know what files are suitable.")

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
            return self.get_id3_reader().release_year

        _date = lastfm_album.get_release_date()
        if not _date:
            if not self.get_id3_reader().release_year:
                return None

            return self.get_id3_reader().release_year

        return datetime.strptime(_date, '%d %b %Y, %H:%M').year

    def save_track(self):
        """
        Takes a path to a track, reads its metadata and stores everything in
        the database.

        """

        full_path = self.file_path.decode('utf-8')

        print(self.file_path)

        track = m.Track(full_path)
        if self.no_metadata:
            self.session.add(track)

            return True
        else:
            if q(m.Track).filter_by(path=full_path).count():
                return True

        use_prev = None
        id3r = self.get_id3_reader()

        artist = self.get_artist(id3r.artist)
        album = self.get_album(id3r.album, artist)

        if artist is not None and artist not in album.artists:
            album.artists.append(artist)

        track.album = album
        track.artist = artist
        self.session.add(track)

        return True

    def get_id3_reader(self):
        if not self.id3r or not self.id3r.same_path(self.file_path):
            self.id3r = ID3Manager(self.file_path)

        return self.id3r

    def is_track(self):
        """Tries to guess whether the file is a valid track or not.
        """
        if os.path.isdir(self.file_path):
            return False

        if '.' not in self.file_path:
            return False

        ext = self.file_path[self.file_path.rfind('.') + 1:]
        if ext not in self.config.get('ACCEPTED_FORMATS', []):
            if self.verbose:
                print(self.file_path + " is not in ACCEPTED_FORMATS")
            return False

        if not self.get_id3_reader().is_valid():
            if self.verbose:
                print(self.file_path + " fails id3 reader")
            return False

        return True

    def walk(self, dir_name):
        """Recursively walks through a directory looking for tracks.
        """

        self.count += 1
        if self.count % 10 == 0:
            self.session.commit()

        if os.path.isdir(dir_name):
            for name in os.listdir(dir_name):
                self.file_path = os.path.join(dir_name, name)
                if os.path.isdir(self.file_path):
                    self.walk(self.file_path)
                else:
                    self.file_count += 1
                    if self.is_track():
                        self.track_count += 1
                        try:
                            self.save_track()
                        except Exception, e:
                            logging.warning("%s not imported - %s" % (
                                self.file_path, e.message))

        return True

    def run(self):
        for mobject in self.media_dirs:
            for mdir in mobject.get_valid_dirs():
                self.walk(mdir)
        if self.verbose:
            print 'Examined {0} files, {1} tracks'.format(self.file_count,
                                                          self.track_count)

if __name__ == '__main__':
    use_lastfm = '--lastfm' in sys.argv
    no_metadata = '--nometadata' in sys.argv
    verbose = '--verbose' in sys.argv or '-v' in sys.argv

    if no_metadata:
        use_lastfm = False

    if use_lastfm and not app.config.get('LASTFM_API_KEY'):
        print('ERROR: You need a Last.FM API key if you set the --lastfm '
              'flag.\n')
        sys.exit(1)

    lola = Indexer(app.config, use_lastfm=use_lastfm, no_metadata=no_metadata,
                   verbose=verbose)
    lola.run()

    # Petit performance hack: Every track will be added to the session but they
    # will be written down to disk only once, at the end.
    lola.session.commit()
