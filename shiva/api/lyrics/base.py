from flask import g, current_app as app

from shiva.api.models import Lyrics
from shiva.utils import _import


class LyricScraper(object):
    """
    """

    def __init__(self, artist, title):
        raise NotImplementedError

    def fetch(self):
        raise NotImplementedError

def get_lyrics(track):
    try:
        scrapers = app.config['SCRAPERS']['lyrics']
    except IndexError, e:
        return None

    for scraper_cls in scrapers:
        Scraper = _import('shiva.api.lyrics.%s' % scraper_cls)
        if issubclass(Scraper, LyricScraper):
            scraper = Scraper(track.artist.name, track.title)
            scraper.fetch()
            if scraper.lyrics:
                lyrics = Lyrics(text=scraper.lyrics, source=scraper.source,
                                track=track)
                g.db.session.add(lyrics)
                g.db.session.commit()

                return lyrics

    return None
