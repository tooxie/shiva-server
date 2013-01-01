# -*- coding: utf-8 -*-
"""
There are 3 types of settings.
1) System. Stays the same for every project.
2) Local. Specific to each instance of the project. Not versioned.
3) Debug. Applies for debugging. Forbidden for production use.
"""
import logging

from shiva.api.config.project import *
try:
    # Rename the file local.py.example to local.py and edit it.
    from shiva.api.config.local import *
except ImportError:
    logging.warning("Couldn't find local settings.")
if DEBUG:
    try:
        from shiva.api.config.debug import *
    except ImportError:
        pass
