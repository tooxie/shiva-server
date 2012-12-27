# -*- coding: utf-8 -*-
# K-Pg
import os
import pickle

import eyed3

from shiva import api, settings

def g(name, value=None):
    gname = '.indexerrc'
    if not os.path.exists(gname):
        with open(gname, 'w') as gfile:
            gfile.write(pickle.dumps({}))

    with open(gname, 'r') as gfile:
        my_globals = pickle.loads(gfile.read())

    if value:
        my_globals.update({name: value})
        with open(gname, 'w') as gfile:
            gfile.write(pickle.dumps(my_globals))
    else:
        if name in my_globals:
            return my_globals[name]

def save_track(file_path):
    """Takes a path to a track, hashes it, reads its metadata and stores
    everything in the database.
    """
    session = api.db.session
    full_path = file_path.decode('utf-8')
    contents_changed = False

    print(file_path)

    if session.query(api.Track).filter_by(path=full_path).count():
        return True

    track = api.Track(full_path)
    session.add(track)

    id3r = track.get_id3_reader()
    if not id3r.tag:
        id3r.tag = eyed3.id3.Tag()

    use_prev = None
    if not id3r.tag.artist:
        _prev = g('PREV_ARTIST')
        if _prev:
            use_prev = raw_input('Use %s? [y/N] ' % _prev).strip()

        if use_prev == 'y':
            _artist = _prev
        else:
            _artist = unicode(raw_input('Artist name: ').strip())

        g('PREV_ARTIST', _artist)
        id3r.tag.artist = _artist
        id3r.tag.save(id3r.path)
        contents_changed = True

    qs_artist = session.query(api.Artist).filter_by(name=id3r.tag.artist)
    if qs_artist.count():
        artist = qs_artist.first()
    else:
        artist = api.Artist(name=id3r.tag.artist)
        session.add(artist)

    use_prev = None
    if not id3r.tag.album:
        _prev = g('PREV_ALBUM')
        if _prev:
            use_prev = raw_input('Use %s? [y/N] ' % _prev).strip()

        if use_prev == 'y':
            _album = _prev
        else:
            _album = unicode(raw_input('Album name: ').strip())

        g('PREV_ALBUM', _album)
        id3r.tag.album = _album
        id3r.tag.save(id3r.path)
        contents_changed = True

    album_year = id3r.tag.release_date.year if id3r.tag.release_date else None
    qs_album = session.query(api.Album).filter_by(name=id3r.tag.album)
    if qs_album.count():
        album = qs_album.first()
    else:
        album = api.Album(name=id3r.tag.album, year=album_year)
        session.add(album)

    album.artist = artist
    session.add(album)

    track.album = album
    if contents_changed:
        track.md5_hash = track.compute_hash()
    session.add(track)

    session.commit()

    return True

def is_track(file_path):
    """Tries to guess whether the file is a valid track or not.
    """

    if os.path.isdir(file_path):
        return False

    if '.' not in file_path:
        return False

    ext = file_path[file_path.rfind('.') + 1:]
    if ext not in getattr(settings, 'ACCEPTED_FORMATS', []):
        return False

    id3data = eyed3.load(file_path)
    if getattr(id3data, 'path', False):
        return True

    return False

def walk(dir_name):
    """Recursively walks through a directory looking for tracks.
    """

    if os.path.isdir(dir_name):
        for name in os.listdir(dir_name):
            path = os.path.join(dir_name, name)
            if os.path.isdir(path):
                walk(path)
            else:
                if is_track(path):
                    save_track(path)
    else:
        if is_track(dir_name):
            save_track(dir_name)

    return True

if __name__ == '__main__':
    media_dirs = getattr(settings, 'MEDIA_DIRS', [])
    if len(media_dirs) == 0:
        print("Remember to set the MEDIA_DIRS setting, otherwise I don't " +
              'know where to look for.')

    for mobject in media_dirs:
        for mdir in mobject.get_dirs():
            walk(mdir)

    if os.path.exists('.indexerrc'):
        os.unlink('.indexerrc')
