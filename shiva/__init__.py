# -*- coding: utf-8 -*-
"""
Shiva is, technically speaking, a RESTful API to your music collection. It
indexes your music and exposes an API with the metadata of your files so you
can then perform queries on it and organize it as you wish.

On a higher level, however, Shiva aims to be a free (as in freedom and beer)
alternative to popular music services. It was born with the goal of giving back
the control over their music and privacy to the users, protecting them from the
industry’s obsession with control.

Read more on: https://hacks.mozilla.org/2013/03/shiva-more-than-a-restful-api-to-your-music-collection/
"""

__version__ = '0.1'
__author__ = u'Alvaro Mouriño'
__contibutors__ = [
    u'Bojan Mihelac <bmihelac@mihelac.org>',
    u'Iago Lastra <iago.lastra@gmail.com>',
    u'Jochen Kupperschmidt <jochen.kupperschmidt@fortytools.com>',
    u'Seth Woodworth <seth@sethish.com>',
    u'Tobias Raeder <tobias.raeder@gmail.com>',
    u'Wieland Hoffmann <themineo+github@gmail.com>',
]


def get_version():
    return __version__


def get_contributors():
    return __contibutors__
