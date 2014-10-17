# Copyright 2014 (C) Rich Wareham
#
# This file is part of Ruaumoko.
# https://github.com/cuspaceflight/ruaumoko
#
# Ruaumoko is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ruaumoko is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ruaumoko. If not, see <http://www.gnu.org/licenses/>.
#
# TemporaryDirectory implementation imported from 3.4.0 Python standard library
# (https://hg.python.org/cpython/file/04f714765c13/Lib/tempfile.py). Copyright
# and distribution terms at
# https://hg.python.org/cpython/file/04f714765c13/LICENSE.
"""Compatibility utilities.

Python 2/3 compatibility shims.
"""
from __future__ import print_function

try:
    from urllib.parse import urlunsplit # py 3
except ImportError:
    from urlparse import urlunsplit # py 2

try:
    from tempfile import TemporaryDirectory
except ImportError:
    import weakref as _weakref
    import shutil as _shutil

    from tempfile import mkdtemp, template

    class TemporaryDirectory(object):
        """Create and return a temporary directory.  This has the same
        behavior as mkdtemp but can be used as a context manager.  For
        example:

            with TemporaryDirectory() as tmpdir:
                ...

        Upon exiting the context, the directory and everything contained
        in it are removed.
        """

        # Handle mkdtemp raising an exception
        name = None
        _finalizer = None
        _closed = False

        def __init__(self, suffix="", prefix=template, dir=None):
            self.name = mkdtemp(suffix, prefix, dir)
            # HACK: work around lack of weakref.finalize in 2.7
            self._self_weakref = _weakref.ref(self, lambda: TemporaryDirectory._cleanup(
                self.name, warn_message="Implicitly cleaning up {!r}".format(self)))

        @classmethod
        def _cleanup(cls, name, warn_message=None):
            _shutil.rmtree(name)
            if warn_message is not None:
                _warnings.warn(warn_message, ResourceWarning)

        def __repr__(self):
            return "<{} {!r}>".format(self.__class__.__name__, self.name)

        def __enter__(self):
            return self.name

        def __exit__(self, exc, value, tb):
            self.cleanup()

        def cleanup(self):
            if self._finalizer is not None:
                self._finalizer.detach()
            if self.name is not None and not self._closed:
                _shutil.rmtree(self.name)
                self._closed = True

