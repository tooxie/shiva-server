import re
import urllib2
import urllib

import lxml.html
import requests
from flask import current_app as app

from shiva.api.lyrics.base import LyricScraper


class MetroLyrics(LyricScraper):
    """
    """

    def __init__(self, artist, title):
        self.artist = urllib2.quote(artist)
        self.title = urllib2.quote(title)
        self.search_url = 'http://www.metrolyrics.com/api/v1/search/artistsong'

        self.lyrics = None
        self.source = None

    def fetch(self):
        self.search()
        if not self.source:
            return None

        print(self.source)
        response = requests.get(self.source)
        html = lxml.html.fromstring(response.text)
        div = html.get_element_by_id('lyrics-body')

        from_re = r'\n\[ From: .*? \]'
        lyrics = re.sub(from_re, '', div.text_content())

        self.lyrics = lyrics.strip()

    def search(self):
        params = {
            'artist': self.artist,
            'song': self.title,
            'X-API-KEY': app.config['METROLYRICS_API_KEY'],
        }
        _url = '?'.join((self.search_url, urllib.urlencode(params)))
        print(_url)
        response = requests.get(_url)
        if response.status_code == 200:
            self.source = response.json()['items'][0]['url']
