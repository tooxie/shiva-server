# -*- coding: utf-8 -*-
from shiva.www import app
from shiva.www import views

app.add_url_rule('/', 'home', views.index)
app.add_url_rule('/artist/<int:pk>/', 'artist', views.artist)
app.add_url_rule('/song/<int:pk>/', 'song', views.song)
app.add_url_rule('/pic/<int:tag_pk>/', 'pic', views.pic)
app.add_url_rule('/stream/<int:song_pk>/', 'stream', views.stream)
app.add_url_rule('/about/', 'about', views.about)
app.add_url_rule('/contact/', 'contact', views.contact)
