import re
import urllib2

import requests
import lxml.html
from slugify import slugify

from shiva.lyrics import LyricScraper
from shiva.utils import get_logger

log = get_logger()


class MP3Lyrics(LyricScraper):
    """
    """

    def __init__(self, artist, title):
        self.artist = artist
        self.title = title
        self.lyrics = None
        self.source = None

        self.search_url = 'http://letrascanciones.mp3lyrics.org/Buscar/%s'
        self.lyric_url_re = re.compile(r'href="(/[a-z0-9]{1}/[a-z0-9\-]+'
                                       r'/[a-z0-9\-]+/)"')
        self.lyric_re = re.compile(r'<div id="lyrics_text" .*?>(.*?)'
                                   r'</div>', re.M + re.S)
        self.title_re = re.compile(r'<title>(?P<title>.*?) Letras de '
                                   r'Canciones de (?P<artist>.*?)</title>')

    def fetch(self):
        self.search()
        if not self.source:
            return None

        response = requests.get(self.source)
        self.html = response.text

        if not self.check():
            return False

        log.info('[FOUND] %s' % self.source)
        self.lyric_re.pattern
        lyrics = self.lyric_re.findall(self.html)[0]
        lyrics = re.sub(r'<span id="findmorespan">.*?</span>', '', lyrics)
        lyrics = re.sub(r'<br[ /]?>', '\r', lyrics)
        lyrics = lyrics[lyrics.find('\r\r'):]

        self.lyrics = lyrics.strip()

        return True

    def search(self):
        query = urllib2.quote('%s %s' % (self.artist, self.title))
        log.info('[SEARCH] %s' % (self.search_url % query))
        response = requests.get(self.search_url % query)
        results = self.lyric_url_re.findall(response.text)

        if results:
            self.source = 'http://letrascanciones.mp3lyrics.org%s' % results[0]

    def check(self):
        match = self.title_re.search(self.html)

        if slugify(match.group('artist')) != slugify(self.artist):
            log.info('%s != %s' % (slugify(match.group('artist')),
                                   slugify(self.artist)))
            return False

        if slugify(match.group('title')) != slugify(self.title):
            log.info('%s != %s' % (slugify(match.group('title')),
                                   slugify(self.title)))
            return False

        return True
