# -*- coding: utf-8 -*-
from shiva.utils import ignored, get_logger

log = get_logger()


class LastFM(object):
    def __init__(self, api_key, use_cache=True):
        """
        Wrapper around LastFM's library, pylast. Simplifies handling and adds
        caching.

        Cache's schema:
            self.cache[artist.name]
            self.cache[artist.name]['object']
            self.cache[artist.name]['albums']
            self.cache[artist.name]['albums'][album.name]
        """
        import pylast

        self.pylast = pylast
        self.use_cache = use_cache
        self.lib = self.pylast.LastFMNetwork(api_key=api_key)
        self.cache = {}

    def get_artist(self, name):
        artist = self.cache.get(name, {}).get('object')

        if not artist:
            log.debug('[ Last.FM ] Retrieving artist "%s"' % name)
            with ignored(Exception, print_traceback=True):
                artist = self.lib.get_artist(name)
            if artist and self.use_cache:
                self.cache.update({
                    name: {
                        'object': artist
                    }
                })

        return artist

    def get_artist_image(self, name):
        image = None

        log.debug('[ Last.FM ] Retrieving artist image for "%s"' % name)
        with ignored(Exception, print_traceback=True):
            image = self.get_artist(name).get_cover_image()

        return image

    def get_album(self, name, artist_name):
        album = self.cache.get(artist_name, {}).get('albums', {}).get(name)

        if not album:
            artist = self.get_artist(artist_name)
            log.debug('[ Last.FM ] Retrieving album "%s" by "%s"' % (
                      name, artist.name))
            with ignored(Exception, print_traceback=True):
                album = self.lib.get_album(artist, name)

            if album and self.use_cache:
                self.cache.update({
                    artist.name: {
                        'albums': {
                            album.name: album
                        }
                    }
                })

        return album

    def get_release_date(self, album_name, artist_name):
        rdate = None
        album = self.get_album(album_name, artist_name)

        if not album:
            return None

        log.debug('[ Last.FM ] album "%s" by "%s" release date' % (
                  album_name, artist_name))
        with ignored(Exception, print_traceback=True):
            rdate = album.get_release_date()
            rdate = datetime.strptime(rdate, '%d %b %Y, %H:%M')

        return rdate

    def get_album_cover(self, album_name, artist_name):
        cover = None
        album = self.get_album(album_name, artist_name)

        if not album:
            return None

        log.debug('[ Last.FM ] Retrieving album "%s" by "%s" cover image' % (
                  album_name, artist_name))
        with ignored(Exception, print_traceback=True):
            cover = album.get_cover_image(size=self.pylast.COVER_EXTRA_LARGE)

        return cover

    def clear_cache(self):
        self.cache = {}
