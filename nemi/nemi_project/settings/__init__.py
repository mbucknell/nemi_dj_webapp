"""
Package contains Django settings for the nemi project. All sensitive
settings and server specific settings should be in the `local` module, which is
not under version control. In particular, any constant that contains passwords
or resources that vary depending on the server should go in the local module.

The `base.py` module contains fallback resources for all essential settings,
and should be imported from `local.py`.
"""

try:
    from .local import *  #pylint: disable=W0401
except ImportError:
    msg = 'Create a local config module in nemi_project/settings/local.py'
    raise NotImplementedError(msg)
