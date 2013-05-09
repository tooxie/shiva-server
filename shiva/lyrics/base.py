from flask import g, current_app as app

from shiva.models import LyricsCache
from shiva.utils import _import


class LyricScraper(object):
    """
    """

    def __init__(self, artist, title):
        self.artist = artist
        self.title = title
        self.lyrics = None
        self.source = None

    def fetch(self):
        raise NotImplementedError

def get_lyrics(track):
    try:
        scrapers = app.config['SCRAPERS']['lyrics']
    except IndexError, e:
        return None

    for scraper_cls in scrapers:
        Scraper = _import('shiva.lyrics.%s' % scraper_cls)
        if issubclass(Scraper, LyricScraper):
            scraper = Scraper(track.artist.name.encode('utf-8'),
                              track.title.encode('utf-8'))
            if scraper.fetch():
                lyrics = LyricsCache(text=scraper.lyrics, track=track,
                                     source=scraper.source)
                g.db.session.add(lyrics)
                g.db.session.commit()

                return lyrics

    return None
