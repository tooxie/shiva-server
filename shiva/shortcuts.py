# -*- coding: utf-8 -*-
from shiva import models
from shiva import settings

from flask import url_for
from sqlalchemy.sql.expression import ClauseElement, alias
from sqlalchemy import distinct

def get_or_create(model, session, defaults={}, **kwargs):
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
        session.commit()

    return (instance, created)

def get_artists():
    """Shortcut to get the list of artists in the DB.
    """

    session = get_session()
    tags = session.query(models.ID3Tag).join(models.TagGroup).\
                   filter(models.TagGroup.name=='performer')
    return session.query(distinct(models.TagContent.string_data), \
            models.TagContent.pk).join(models.SongTag).join(tags)

def get_songs_for_artist(artist):
    """Get a list of Song objects for a given artist. The function expects a
    TagContent object that contains an artist name.
    """

    session = get_session()
    if type(artist) == int:
        artist = session.query(models.TagContent).filter_by(pk=artist).one()
    return session.query(models.Song).join(models.SongTag).join(models.TagContent).\
                   filter(models.SongTag.content==artist)

def get_song(pk):
    """
    """

    session = get_session()
    song = session.query(models.Song).filter_by(pk=pk).one()
    tags = session.query(models.TagContent).join(models.SongTag).\
                      filter(models.SongTag.song==song)
    title = tags.join(session.query(models.ID3Tag).join(models.TagGroup).\
                 filter(models.TagGroup.name=='title')).first()
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
