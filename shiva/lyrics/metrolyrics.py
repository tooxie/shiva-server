import re
import urllib2
import urllib

import lxml.html
import requests
from flask import current_app as app

from shiva.lyrics import LyricScraper
from shiva.utils import get_logger

log = get_logger()


class MetroLyrics(LyricScraper):
    """
    """

    def __init__(self, artist, title):
        self.artist = artist
        self.title = title
        self.search_url = 'http://www.metrolyrics.com/api/v1/search/artistsong'
        self.title_re = re.compile(r'<title>(?P<artist>.*?) - '
                                   r'(?P<title>.*?) LYRICS</title>')

        self.lyrics = None
        self.source = None

    def fetch(self):
        self.search()
        if not self.source:
            return None

        response = requests.get(self.source)
        self.html = response.text
        html = lxml.html.fromstring(self.html)

        if not self.check():
            return False

        log.info('[FOUND] %s' % self.source)
        div = html.get_element_by_id('lyrics-body')
        lyrics = re.sub(r'\n\[ From: .*? \]', '', div.text_content())

        self.lyrics = lyrics.strip()

        return True

    def search(self):
        params = {'artist': self.artist,
                  'song': self.title,
                  'X-API-KEY': app.config['METROLYRICS_API_KEY']}
        _url = '?'.join((self.search_url, urllib.urlencode(params)))
        log.info('[SEARCH] %s' % _url)
        response = requests.get(_url)
        if response.status_code == 200:
            self.source = response.json()['items'][0]['url']

    def check(self):
        match = self.title_re.search(self.html)

        if match.group('artist').lower() != self.artist.lower():
            return False

        if match.group('title').lower() != self.title.lower():
            return False

        return True
