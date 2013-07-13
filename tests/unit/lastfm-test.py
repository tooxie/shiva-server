# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except ImportError:
    import unittest
from mock import Mock, patch

from shiva.indexer.lastfm import LastFM


class LastFMTestCase(unittest.TestCase):

    def setUp(self):
        import sys
        sys.modules["pylast"] = Mock()

        api_key = 'FAKE_API_KEY'
        self.lastfm = LastFM(api_key)

    def test_caches_artists(self):
        artist = self.lastfm.get_artist('Artist')

        self.assertEqual(self.lastfm.get_artist('Artist'), artist)
        self.assertEqual(self.lastfm.cache, {
            'Artist': {
                'object': artist
            }
        })

    def test_clear_cache(self):
        self.lastfm.get_artist('Artist')
        _cache = self.lastfm.cache
        self.lastfm.clear_cache()

        self.assertNotEqual(self.lastfm.cache, _cache)

    def test_caches_albums(self):
        artist = self.lastfm.get_artist('Artist')
        artist.name = 'Artist'

        album = self.lastfm.get_album('Album name', 'Artist')
        album.name = 'Album name'

        self.assertEqual(self.lastfm.get_album('Album name', 'Artist'), album)
        self.assertEqual(self.lastfm.cache, {
            'Artist': {
                'albums': {
                    'Album name': album
                }
            }
        })
