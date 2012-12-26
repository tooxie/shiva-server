# -*- coding: utf-8 -*-
from shiva import settings

from sqlalchemy.sql.expression import ClauseElement

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
