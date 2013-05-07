import re
import urllib2

import requests

from shiva.lyrics import LyricScraper
from shiva.utils import get_logger

log = get_logger()


class AZLyrics(LyricScraper):
    """
    """

    def __init__(self, artist, title):
        self.artist = artist
        self.title = title
        self.lyrics = None
        self.source = None

        self.search_url = 'http://search.azlyrics.com/search.php?q=%s'
        self.lyric_url_re = re.compile(r'http://www\.azlyrics\.com/lyrics/'
                                       r'[a-z0-9]+/[a-z0-9]+\.html')
        self.lyric_re = re.compile(r'<!-- start of lyrics -->(.*)'
                                   r'<!-- end of lyrics -->', re.M + re.S)
        self.title_re = re.compile(r'<title>(?P<artist>.*?) LYRICS - '
                                   r'(?P<title>.*?)</title>')

    def fetch(self):
        self.search()
        if not self.source:
            return None

        response = requests.get(self.source)
        self.html = response.text

        if not self.check():
            return False

        log.info('[FOUND] %s' % self.source)
        lyrics = self.lyric_re.findall(self.html)[0]
        lyrics = re.sub(r'<br[ /]?>', '\r', lyrics)
        lyrics = re.sub(r'<.*?>', '', lyrics)

        self.lyrics = lyrics.strip()

        return True

    def search(self):
        query = urllib2.quote('%s %s' % (self.artist, self.title))
        log.info('[SEARCH] %s' % (self.search_url % query))
        response = requests.get(self.search_url % query)
        results = self.lyric_url_re.findall(response.text)

        if results:
            self.source = results[0]

    def check(self):
        match = self.title_re.search(self.html)

        if match.group('artist').lower() != self.artist.lower():
            return False

        if match.group('title').lower() != self.title.lower():
            return False

        return True
