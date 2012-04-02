# -*- coding: utf-8 -*-
from shiva import settings

from flask import url_for
from sqlalchemy import (Boolean, Column, ForeignKey, Integer, LargeBinary,
                        Sequence, String,)
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref
import os

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, echo=True)
Session = sessionmaker(bind=engine)

# ATTENTION: Next line is the worst hack to bypass this exception:
# AttributeError: 'Sequence' object has no attribute 'arg'
# It's thrown in flask_admin/datastore/sqlalchemy.py:250 when exclude_pks is
# set to False on flask.ext.admin.datastore.sqlalchemy.SQLAlchemyDatastore.
Sequence.arg = None  # HACK ALERT
# Sorry you had to see that. Let's try to get over it and move on.

def get_session():
    return Session()

Base = declarative_base()


class Hash(Base):
    """A Hash of a file, to recognize duplicated songs.
    """

    __tablename__ = 'hashes'

    digest = Column(String(32), primary_key=True)  # md5

    def __repr__(self):
        return "<Hash('%s')>" % self.digest


class Song(Base):
    """A music file, generally an mp3 file.
    """

    __tablename__ = 'songs'

    pk = Column(Integer, Sequence('song_pk'), primary_key=True)
    path = Column(String(128))
    hash_pk = Column(Integer, ForeignKey('hashes.digest'))
    size = Column(Integer)

    hash = relationship('Hash', backref=backref('songs', order_by=pk))

    def get_url(self):
        from shiva.shortcuts import get_song_url

        return get_song_url(self)

    def __repr__(self):
        return "<Song('%s')>" % self.path


class TagGroup(Base):
    """When many different tags mean the same things - which is the case with
    'TIT2', 'TT2' and 'v1title', they all refer to the song title - groups can
    be used to define that relationship.
    """

    __tablename__ = 'taggroups'

    name = Column(String(128), primary_key=True)

    def __repr__(self):
        return "<TagGroup('%s')>" % self.name


class ID3Tag(Base):
    """ID3 is a metadata container most often used in conjunction with the MP3
    audio file format. It allows information such as the title, artist, album,
    track number, and other metadata about the file to be stored in the file
    itself.
    """

    __tablename__ = 'tags'

    pk = Column(Integer, Sequence('tag_pk'), primary_key=True)
    name = Column(String(128))
    group_pk = Column(String, ForeignKey('taggroups.name'))

    group = relationship('TagGroup', backref=backref('tags', order_by=pk))

    def __repr__(self):
        group = ''
        if self.group:
            group = ", '%s'" % self.group.name
        return "<ID3Tag('%s'%s)>" % (self.name, group)


class TagContent(Base):
    """The actual contents of a given tag. This is a separate model because
    many songs share album, artist, album art, etc...
    """

    __tablename__ = 'contents'

    pk = Column(Integer, Sequence('content_pk'), primary_key=True)
    is_binary = Column(Boolean)
    binary_data = Column(LargeBinary)
    string_data = Column(String(256))

    def __repr__(self):
        if self.is_binary:
            return "<TagContent(#%d) Binary>" % (self.pk)
        else:
            return "<TagContent(#%d, '%s')>" % (self.pk, self.string_data)

    def get_contents(self):
        if self.is_binary:
            return self.binary_data
        else:
            return self.string_data


class SongTag(Base):
    """The relationship between the song, the tag and its contents.
    """

    __tablename__ = 'songtags'

    pk = Column(Integer, Sequence('songtag_pk'), primary_key=True)
    song_pk = Column(Integer, ForeignKey('songs.pk'))
    tag_pk = Column(Integer, ForeignKey('tags.pk'))
    content_pk = Column(Integer, ForeignKey('contents.pk'))

    song = relationship('Song', backref=backref('tags', order_by=pk))
    tag = relationship('ID3Tag', backref=backref('songs', order_by=pk))
    content = relationship('TagContent',
                           backref=backref('contents', order_by=pk))

    def get_contents(self):
        return self.content.get_contents()

Base.metadata.create_all(engine)
