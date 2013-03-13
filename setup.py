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
    install_requires=[
        'Flask==0.9',
        'Flask-Restful==0.1.2',
        'Flask-SQLAlchemy==0.16',
        'eyed3==0.7.1',
        'requests==1.0.4',
        'translitcodec==0.3',
        'pyLast==0.5.11',
        'lxml==3.1beta1'
    ],
    entry_points={
        'console_scripts': [
            'shiva-server = shiva.app:main'
        ]
    }
)
