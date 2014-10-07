# -*- coding: utf-8 -*-
from shiva.admin import main as admin
from shiva.app import main as server
from shiva.fileserver import main as fileserver
from shiva.indexer import main as indexer

__all__ = [admin, server, fileserver, indexer]
