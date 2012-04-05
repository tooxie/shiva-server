# -*- coding: utf-8 -*-
# K-Pg
from shiva import models
from shiva.shortcuts import get_or_create
from shiva import settings

from hashlib import md5
import id3reader
import os
import unicodedata

def _safestr(s):
    """Translate any string into a safe unicode string.
    """

    if type(s) == str:
        return unicodedata.normalize('NFC', unicode(s, encoding='latin1',
                                                    errors='ignore'))

    return s

def compute_hash(file_path):
    """Computes the hash for a file.
    """

    return md5(open(file_path, 'r').read()).hexdigest()

def file_size(file_path):
    """Returns the size of a file.
    """

    return os.stat(file_path).st_size

def save_song(file_path):
    """Takes a path to a song, hashes it, reads its metadata and stores
    everything in the database.
    """

    full_path = _safestr(os.path.abspath(file_path))
    id3data = id3reader.Reader(file_path)
    session = models.get_session()

    if session.query(models.Song).filter_by(path=full_path).count():
        return True

    song_hash, c = get_or_create(session, models.Hash,
                                        digest=compute_hash(file_path))
    song, c = get_or_create(session, models.Song, path=full_path,
                                   hash=song_hash, size=file_size(file_path))
    for frame in id3data.allFrames:
        tag, c = get_or_create(session, models.ID3Tag, name=frame.id)
        if hasattr(frame, 'value'):
            value = frame.value if type(frame.value) != list else ''
            params = {'string_data': _safestr(value), 'is_binary': False}
        else:
            params = {'binary_data': frame.rawData, 'is_binary': True}
        data, c = get_or_create(session, models.TagContent, **params)
        session.add(data)
        song_tag = models.SongTag(song=song, tag=tag, content=data)
        session.add(song_tag)
    session.commit()

def is_song(file_path):
    """Tries to guess whether the file is a valid song or not.
    """

    if os.path.isdir(file_path):
        return False
    if '.' not in file_path:
        return False
    ext = file_path[file_path.rfind('.') + 1:]
    if ext not in getattr(settings, 'ACCEPTED_FORMATS', []):
        return False
    id3data = None
    try:
        id3data = id3reader.Reader(file_path)
    except Exception, e:
        return False
    if id3data:
        return True
    return False

def walk(dir_name):
    """Recursively walks through a directory looking for songs.
    """

    if os.path.isdir(dir_name):
        for name in os.listdir(dir_name):
            path = os.path.join(dir_name, name)
            if os.path.isdir(path):
                walk(path)
            else:
                if is_song(path):
                    save_song(path)
    else:
        if is_song(dir_name):
            save_song(dir_name)

    return True

if __name__ == '__main__':
    media_dirs = getattr(settings, 'MEDIA_DIRS', [])
    if len(media_dirs) == 0:
        print("Remember to set the MEDIA_DIRS setting, otherwise I don't " +
              'know where to look for.')

    for mobject in media_dirs:
        for mdir in mobject.get_dirs():
            walk(mdir)
