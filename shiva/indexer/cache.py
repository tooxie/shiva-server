# -*- coding: utf-8 -*-
from sqlalchemy.orm.exc import NoResultFound

from shiva import models as m
from shiva.app import db
from shiva.utils import get_logger

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
        self.hashes = set()

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

    def add_hash(self, hash):
        if self.ram_cache:
            self.hashes.add(hash)

    def hash_exists(self, hash):
        if hash in self.hashes:
            return True

        if self.use_db:
            return bool(q(m.Track).filter_by(hash=hash).count())

        return False

    def clear(self):
        self.artists = {}
        self.albums = {}
        self.hashes = set()
