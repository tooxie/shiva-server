# -*- coding: utf-8 -*-
# Shiva - A RESTful API to your music collection
#
# Copyright © 2014 Alvaro Mouriño
# Author: Alvaro Mouriño <alvaro@mourino.net>
# URL: <https://github.com/tooxie/shiva-server>
"""
Shiva
=====

Shiva is, technically speaking, a RESTful API to your music collection. It
indexes your music and exposes an API with the metadata of your files so you
can then perform queries on it and organize it as you wish.

On a higher level, however, Shiva aims to be a free (as in freedom and beer)
alternative to popular music services. It was born with the goal of giving back
the control over their music and privacy to the users, protecting them from the
industry’s obsession with control.

It’s not intended to compete directly with online music services, but to be an
alternative that you can install and modify to your needs. You will own the
music in your server. Nobody but you (or whoever you give permission) will be
able to delete files or modify the files’ metadata to correct it when it’s
wrong. And of course, it will all be available to any device with Internet
connection.

You will also have a clean, RESTful API to your music without restrictions. You
can grant access to your friends and let them use the service or, if they have
their own Shiva instances, let both servers talk to each other and share the
music transparently.

To sum up, Shiva is a distributed social network for sharing music.

Read more on https://hacks.mozilla.org/2013/03/shiva-more-than-a-restful-api-\
to-your-music-collection/

Copyright © 2014 Alvaro Mouriño
"""

__version__ = '0.9.0'
__author__ = u'Alvaro Mouriño'
__author_email__ = 'alvaro@mourino.net'
__copyright__ = '2014 Alvaro Mouriño'
__url__ = 'https://github.com/tooxie/shiva-server'
__contributors__ = [
    u'Bojan Mihelac <bmihelac@mihelac.org>',
    u'Danilo Bargen <gezuru@gmail.com>',
    u'Felix Hummel <felix@felixhummel.de>',
    u'Iago Lastra <iago.lastra@gmail.com>',
    u'Jochen Kupperschmidt <jochen.kupperschmidt@fortytools.com>',
    u'Kevin Poorman <kjp@brightleafsoftware.com>',
    u'Manuel Díez <manutenfruits@gmail.com>',
    u'Sean Lang <slang800@gmail.com>',
    u'Seth Woodworth <seth@sethish.com>',
    u'Tobias Raeder <tobias.raeder@gmail.com>',
    u'Wieland Hoffmann <themineo+github@gmail.com>',
]


def get_version():
    return __version__


def get_contributors():
    return __contributors__
