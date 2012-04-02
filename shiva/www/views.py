# -*- coding: utf-8 -*-
from shiva.www import app
from shiva.shortcuts import (get_artists, get_songs_for_artist, get_song,
                             allowed_to_stream)
from shiva.models import get_session, TagContent, Song, SongTag

from flask import abort, render_template, send_file, Response
import os

def index():
    """
    """

    return render_template('index.html', artists=get_artists())

def artist(pk):
    """
    """

    artist = get_session().query(TagContent).filter_by(pk=pk).one()
    return render_template('artist.html', artist=artist.string_data,
                                          songs=get_songs_for_artist(artist))

def song(pk):
    """
    """

    song, title, tags = get_song(pk)
    # If the song is not under one of the MEDIA_DIRS directories access to it
    # is denied.
    if not allowed_to_stream(song):
        abort(401)
    return render_template('song.html', song=song, song_title=title, tags=tags)

def stream(song_pk):
    """
    """

    song = get_session().query(Song).filter_by(pk=song_pk).one()
    response = send_file(song.path)
    response.headers.add('Content-Length', str(os.path.getsize(song.path)))

    return response

def pic(tag_pk):
    """
    """

    tag = get_session().query(TagContent).filter_by(pk=tag_pk).one()
    response = Response(response=tag.get_contents(), status=200,
                        mimetype='image/jpg')

    return response

def about():
    """
    """

    return render_template('about.html')

def contact():
    """
    """

    return render_template('contact.html')
