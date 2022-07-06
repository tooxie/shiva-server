#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

import shiva

setup(
    name='shiva',
    version=shiva.__version__,
    description='A RESTful API to your music collection',
    long_description=shiva.__doc__,
    author=u'Alvaro Mouriño',
    author_email='alvaro@mourino.net',
    url=shiva.__url__,
    download_url='https://codeload.github.com/tooxie/shiva-server/zip/master',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2 :: Only',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python',
        'Topic :: Communications :: File Sharing',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Multimedia',
    ],
    license='MIT',
    platforms=['OS-independent', 'Any'],
    package_dir={'': '.'},
    packages=find_packages('.'),
    package_data={
        "shiva": [
            "logging.conf",
        ]
    },
    install_requires=[
        'bcrypt==1.0.2',
        'docopt==0.6.1',
        'Flask-Compress==1.1.0',
        'Flask-Restful==0.2.3',
        'Flask-SQLAlchemy==0.16',
        'Flask==0.10',
        'lxml==4.9.1',
        'mutagen==1.21',
        'pyLast==0.5.11',
        'python-dateutil==2.1',
        'python-slugify==0.0.3',
        'requests==1.0.4',
    ],
    entry_points={
        'console_scripts': [
            'shiva-admin = shiva.bin:admin',
            'shiva-fileserver = shiva.bin:fileserver',
            'shiva-indexer = shiva.bin:indexer',
            'shiva-server = shiva.bin:server',
        ]
    }
)
