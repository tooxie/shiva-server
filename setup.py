#!/usr/bin/env python

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
    entry_points={
        'console_scripts': [
            'shiva-server = shiva.app:main'
        ]
    }
)
