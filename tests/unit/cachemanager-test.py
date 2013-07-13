# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from shiva.indexer.cache import CacheManager


class MockArtist(object):
    """ Mock artist """

    def __init__(self, name):
        self.name = name


class MockAlbum(object):
    """ Mock album """

    def __init__(self, name):
        self.name = name


class CacheManagerTestCase(unittest.TestCase):

    def setUp(self):
        self.cache = CacheManager(use_db=False)

    def test_non_existent_artist(self):
        self.assertIsNone(self.cache.get_artist('NQH'))

    def test_save_artist(self):
        pirexia = MockArtist('Pirexia')
        self.cache.add_artist(pirexia)

        self.assertIs(self.cache.get_artist('Pirexia'), pirexia)

    def test_save_album(self):
        fun_people = MockArtist('Fun People')
        kum_kum = MockAlbum('Kum Kum')

        self.cache.add_album(kum_kum, fun_people)

        self.assertIs(self.cache.get_album('Kum Kum', fun_people),
                      kum_kum)

    def test_clear(self):
        eterna = MockArtist('Eterna Inocencia')
        ei = MockAlbum('EI')

        self.cache.add_artist(eterna)
        self.cache.add_album(ei, eterna)

        self.cache.clear()

        self.assertIsNone(self.cache.get_artist('Eterna Inocencia'))
        self.assertIsNone(self.cache.get_album('EI', eterna))

    def test_no_ram_cache(self):
        cache = CacheManager(ram_cache=False, use_db=False)
        rudos = MockArtist('Rudos Wild')
        cache.add_artist(rudos)

        self.assertIsNone(cache.get_artist('Rudos Wild'))
