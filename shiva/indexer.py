# -*- coding: utf-8 -*-
# K-Pg
import os
import pickle
from datetime import datetime

import eyed3
import pylast

from shiva import api, settings

def get_lastfm_api_key():
    return file('lastfm.key', 'r').read().strip()


class ID3Manager(object):
    def __init__(self, mp3_path):
        self.mp3_path = mp3_path
        self.reader = eyed3.load(mp3_path)

        if not self.reader.tag:
            self.reader.tag = eyed3.id3.Tag()
            self.reader.tag.save(mp3_path)

    def __getattribute__(self, attr):
        _super = super(ID3Manager, self)
        try:
            _getter = _super.__getattribute__('get_%s' % attr)
        except AttributeError:
            _getter = None
        if _getter:
            return _getter()

        return super(ID3Manager, self).__getattribute__(attr)

    def __setattr__(self, attr, value):
        value = value.strip() if isinstance(value, (str, unicode)) else value
        _setter = getattr(self, 'set_%s' % attr, None)
        if _setter:
            _setter(value)

        super(ID3Manager, self).__setattr__(attr, value)

    def is_valid(self):
        if not self.reader.path:
            return False

        return True

    def get_path(self):
        return self.mp3_path

    def same_path(self, path):
        return path == self.mp3_path

    def get_artist(self):
        return self.reader.tag.artist.strip()

    def set_artist(self, name):
        self.reader.tag.artist = name
        self.reader.tag.save()

    def get_album(self):
        return self.reader.tag.album.strip()

    def set_album(self, name):
        self.reader.tag.album = name
        self.reader.tag.save()

    def get_release_year(self):
        rdate = self.reader.tag.release_date
        return rdate.year if rdate else None

    def set_release_year(self, year):
        self.release_date.year = year
        self.reader.tag.save()


class Indexer(object):
    def __init__(self, settings=None):
        self.settings = settings
        self.media_dirs = getattr(self.settings, 'MEDIA_DIRS', [])
        self.id3r = None
        self.PREV_ARTIST = None
        self.PREV_ALBUM = None
        self.lastfm = pylast.LastFMNetwork(api_key=get_lastfm_api_key())

        if len(self.media_dirs) == 0:
            print('Remember to set the MEDIA_DIRS setting, otherwise I ' +
                  'don\'t know where to look for.')

    def get_artist(self, name):
        artist = api.db.session.query(api.Artist).filter_by(name=name).first()
        if not artist:
            cover = self.lastfm.get_artist(name).get_cover_image()
            artist = api.Artist(name=name, image=cover)
            api.db.session.add(artist)
            api.db.session.commit()

        return artist

    def get_release_year(self, lastfm_album):
        _date = lastfm_album.get_release_date()
        if not _date:
            return None

        return datetime.strptime(_date, '%d %b %Y, %H:%M').year

    def check_diff(self, track_obj):
        changed = False
        id3r = self.get_id3_reader()
        if id3r.tag.artist != track_obj.album.artist.name:
            print('%s != %s' % (id3r.tag.artist, track_obj.album.artist.name))
            if not id3r.tag.artist:
                id3r.tag.artist = track_obj.album.artist.name
                id3r.tag.save()
                changed = True

            elif not track_obj.album.artist.name:
                track_obj.album.artist.name = id3r.tag.artist
                api.db.session.add(track_obj.album.artist)
                changed = True

            else:
                print(id3r.path)
                print(track_obj.path)
                print('Chose one:')
                print('1) %s' % id3r.tag.artist)
                print('2) %s' % track_obj.album.artist.name)
                print('w) Other')
                print('i) Ignore')
                option = unicode(raw_input('Chose 1, 2, w or q: '))
                if option == '1':
                    print('You chose %s' % id3r.tag.artist)
                    track_obj.album.artist = self.get_artist(id3r.tag.artist)
                    api.db.session.add(track_obj.album)
                    changed = True
                elif option == '2':
                    print('You chose %s' % track_obj.album.artist.name)
                    id3r.tag.artist = track_obj.album.artist.name
                    id3r.tag.save()
                    changed = True
                elif option == 'w':
                    _artist = self.get_artist(raw_input('Artist name: '))
                    id3r.tag.artist = _artist.name
                    id3r.tag.save()
                    track_obj.album.artist = _artist
                    api.db.session.add(track_obj.album)
                    changed = True

            if changed:
                api.db.session.add(track_obj)
                api.db.session.commit()

    def save_track(self):
        """Takes a path to a track, reads its metadata and stores everything in
        the database.
        """
        session = api.db.session
        full_path = self.file_path.decode('utf-8')

        print(self.file_path)

        if session.query(api.Track).filter_by(path=full_path).count():
            return True

        track = api.Track(full_path)
        session.add(track)

        use_prev = None
        id3r = self.get_id3_reader()
        if not id3r.artist:
            _prev = self.PREV_ARTIST
            if _prev:
                use_prev = raw_input('Use %s? [y/N] ' % _prev).strip()

            if use_prev == 'y':
                _artist = _prev
            else:
                _artist = unicode(raw_input('Artist name: ').strip())

            self.PREV_ARTIST = _artist
            id3r.artist = _artist

        use_prev = None
        if not id3r.album:
            _prev = self.PREV_ALBUM
            if _prev:
                use_prev = raw_input('Use %s? [y/N] ' % _prev).strip()

            if use_prev == 'y':
                _album = _prev
            else:
                _album = unicode(raw_input('Album name: ').strip())

            self.PREV_ALBUM = _album
            id3r.album = _album

        artist = self.get_artist(id3r.artist)

        album = api.Album.query.filter_by(name=id3r.album).first()
        # album = qs_album.intersect(artist.albums).first()
        if not album:
            album = api.Album(name=id3r.album, year=id3r.release_year)
            _album = self.lastfm.get_album(self.lastfm.get_artist(artist.name),
                                           album.name)
            album.cover = _album.get_cover_image(size=pylast.COVER_EXTRA_LARGE)
            album.year = self.get_release_year(_album)

        if artist not in album.artists:
            album.artists.append(artist)

        session.add(album)

        track.album = album
        session.add(track)

        session.commit()

        return True

    def get_id3_reader(self):
        if not self.id3r:
            self.id3r = ID3Manager(self.file_path)

        if not self.id3r.same_path(self.file_path):
            self.id3r = ID3Manager(self.file_path)

        return self.id3r

    def is_track(self):
        """Tries to guess whether the file is a valid track or not.
        """
        if os.path.isdir(self.file_path):
            return False

        if '.' not in self.file_path:
            return False

        ext = self.file_path[self.file_path.rfind('.') + 1:]
        if ext not in getattr(self.settings, 'ACCEPTED_FORMATS', []):
            return False

        if not self.get_id3_reader().is_valid():
            return False

        return True

    def walk(self, dir_name):
        """Recursively walks through a directory looking for tracks.
        """

        if os.path.isdir(dir_name):
            for name in os.listdir(dir_name):
                self.file_path = os.path.join(dir_name, name)
                if os.path.isdir(self.file_path):
                    self.walk(self.file_path)
                else:
                    if self.is_track():
                        self.save_track()
        else:
            self.file_path = dir_name
            if self.is_track():
                self.save_track()

        return True

    def run(self):
        for mobject in self.media_dirs:
            for mdir in mobject.get_dirs():
                self.walk(mdir)

if __name__ == '__main__':
    lola = Indexer(settings)
    lola.run()
