# -*- coding: utf-8 -*-
"""
There are 3 types of settings.
1) System. Stays the same for every project.
2) Local. Specific to each instance of the project. Not versioned.
3) Debug. Applies for debugging. Forbidden for production use.
"""
from shiva.config.project import *
from shiva.utils import ignored

with ignored(ImportError):
    from shiva.config.local import *

if DEBUG:
    with ignored(ImportError):
        from shiva.config.debug import *
