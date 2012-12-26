# -*- coding: utf-8 -*-
# K-Pg
from shiva import api
from shiva.shortcuts import get_or_create
from shiva import settings

import os
import eyed3

def save_track(file_path):
    """Takes a path to a track, hashes it, reads its metadata and stores
    everything in the database.
    """
    session = api.db.session
    full_path = file_path.decode('utf-8')

    if session.query(api.Track).filter_by(path=full_path).count():
        return True

    track, created = get_or_create(api.Track, session=session,
                                  path=full_path)

    id3r = track.get_id3_reader().tag
    artist, created = get_or_create(api.Artist, session=session,
                                    name=id3r.artist)
    album, created = get_or_create(api.Album, session=session, name=id3r.album,
                                   year=id3r.release_date)

    album.artist = artist
    session.add(album)

    track.album = album
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
