# Copyright 2014 (C) Priyesh Patel, Daniel Richman
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

import sys

from setuptools import setup, Extension

try:
     from Cython.Build import cythonize
     cython_present = True
except ImportError:
     cython_present = False

if cython_present:
    ext_modules = cythonize("ruaumoko/dataset.pyx")
else:
    ext_modules = [Extension('ruaumoko.dataset', ['ruaumoko/dataset.c'])]

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    long_description = ''

def get_version():
    with open("ruaumoko/__init__.py") as f:
        for line in f:
            if line.startswith("__version__"):
                return line[15:-2]
    raise Exception("Could not find version number")

console_scripts = [
    "ruaumoko-api = ruaumoko.manager:main",
    "ruaumoko-get = ruaumoko.get_cmd:main",
    "ruaumoko-download = ruaumoko.download:main",
    "ruaumoko-ascii-map = ruaumoko.asciiart:main",
]

setup(
    name="Ruaumoko",
    version=get_version(),
    author='Cambridge University Spaceflight',
    author_email='contact@cusf.co.uk',
    packages=['ruaumoko'],
    entry_points={"console_scripts": console_scripts},
    ext_modules=ext_modules,
    url='http://www.cusf.co.uk/wiki/ruaumoko',
    license='GPLv3+',
    description='Ground Elevation API',
    long_description=long_description,
    install_requires=[
        # Web API
        "Flask",
        "Flask-Script",

        # Command line processing
        "docopt",

        # Core functionality
        "magicmemoryview",

        # Downloader
        "sh", "requests",
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.3',
        'Topic :: Scientific/Engineering',
    ],
)
