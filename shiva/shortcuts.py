# -*- coding: utf-8 -*-
from shiva.models import *

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
