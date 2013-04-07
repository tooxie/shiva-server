#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='Shiva',
    version='0.1.0',
    description='A RESTful API to your music collection',
    author=u'Alvaro Mouriño',
    author_email='alvaro@mourino.net',
    url='https://github.com/tooxie/shiva-server',
    package_dir={'': '.'},
    packages=find_packages('.'),
    install_requires=[
        'docopt==0.6.1',
        'Flask-Restful==0.1.2',
        'Flask-SQLAlchemy==0.16',
        'Flask==0.9',
        'lxml==3.1beta1',
        'mutagen==1.21',
        'pyLast==0.5.11',
        'python-dateutil==2.1',
        'python-slugify==0.0.3',
        'requests==1.0.4',
        'translitcodec==0.3',
    ],
    entry_points={
        'console_scripts': [
            'shiva-server = shiva.app:main',
            'shiva-indexer = shiva.indexer:main'
        ]
    }
)
