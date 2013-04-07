from datetime import datetime

from lxml import etree
import requests

from shiva.models import Artist


class ShowModel(object):
    """
    Mock model that encapsulates the show logic for converting a JSON structure
    into an object.

    """

    def __init__(self, artist, json):
        self.json = json
        self.id = json['id']
        self.artists, self.other_artists = self.split_artists(json['artists'])
        self.datetime = self.to_datetime(json['datetime'])
        self.title = json['title']
        self.tickets_left = (json['ticket_status'] == 'available')
        self.venue = json['venue']

    def split_artists(self, json):
        if len(json) == 0:
            ([], [])
        elif len(json) == 1:
            artist = Artist.query.filter_by(name=json[0]['name']).first()

            return ([artist], [])

        my_artists = []
        other_artists = []
        for artist_dict in json:
            artist = Artist.query.filter_by(name=artist_dict['name'])
            if artist.count():
                my_artists.append(artist.first())
            else:
                del artist_dict['thumb_url']
                other_artists.append(artist_dict)

        return (my_artists, other_artists)

    def to_datetime(self, timestamp):
        return datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S')

    def get_mbid(self, artist):
        mb_uri = 'http://musicbrainz.org/ws/2/artist?query=%(artist)s' % {
            'artist': urllib2.quote(artist)
        }

        logger.info(mb_uri)

        response = requests.get(mb_uri)
        mb_xml = etree.fromstring(response.text)
        # /root/artist-list/artist.id
        artist_list = mb_xml.getchildren()[0].getchildren()
        if artist_list:
            return artist_list[0].get('id')

        return None

    def __getitem__(self, key):
        return getattr(self, key, None)
