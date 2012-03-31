# -*- coding: utf-8 -*-
from shiva.www import app
from shiva.shortcuts import get_artists, get_songs_for_artist
from shiva.models import get_session, TagContent
from flask import render_template

def index():
    return render_template('index.html', artists=get_artists())

def artist(pk):
    artist = get_session().query(TagContent).filter_by(pk=pk).one()
    return render_template('artist.html', artist=artist.string_data,
                                          songs=get_songs_for_artist(artist))

def about():
    return render_template('about.html')

def contact():
    return render_template('contact.html')
