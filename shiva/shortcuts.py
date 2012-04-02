# -*- coding: utf-8 -*-
from shiva.models import *
from shiva import settings

from flask import url_for
from sqlalchemy.sql.expression import ClauseElement, alias
from sqlalchemy import distinct

def get_or_create(session, model, defaults={}, **kwargs):
    """Django's get_or_create implementation for SQLAlchemy.
    """

    created = False
    instance = session.query(model).filter_by(**kwargs).first()
    if not instance:
        params = dict((k, v) for k, v in kwargs.iteritems() \
                             if not isinstance(v, ClauseElement))
        params.update(defaults)
        instance = model(**params)
        session.add(instance)
        created = True

    return (instance, created)

def get_artists():
    """Shortcut to get the list of artists in the DB.
    """

    session = get_session()
    tags = session.query(ID3Tag).join(TagGroup).\
                   filter(TagGroup.name=='performer')
    return session.query(distinct(TagContent.string_data), TagContent.pk).\
            join(SongTag).join(tags)

def get_songs_for_artist(artist):
    """Get a list of Song objects for a given artist. The function expects a
    TagContent object that contains an artist name.
    """

    session = get_session()
    if type(artist) == int:
        artist = session.query(TagContent).filter_by(pk=artist).one()
    return session.query(Song).join(SongTag).join(TagContent).\
                   filter(SongTag.content==artist)

def get_song(pk):
    """
    """

    session = get_session()
    song = session.query(Song).filter_by(pk=pk).one()
    tags = session.query(TagContent).join(SongTag).\
                      filter(SongTag.song==song)
    title = tags.join(session.query(ID3Tag).join(TagGroup).\
                 filter(TagGroup.name=='title')).first()
    try:
        title = title.string_data
    except AttributeError:
        title = ''
    return (song, title, tags)

def get_song_url(song):
    """
    """

    for mobject in getattr(settings, 'MEDIA_DIRS', []):
        url = mobject.get_song_url(song)
        if url:
            return url

    # It really should never hit this line. But you know...
    return url_for('stream', song_pk=song.pk)

def allowed_to_stream(song):
    """
    """

    for mobject in getattr(settings, 'MEDIA_DIRS', []):
        if mobject.allowed_to_stream(song):
            return True

    return False
