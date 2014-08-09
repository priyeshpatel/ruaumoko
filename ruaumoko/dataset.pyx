# Copyright 2014 (C) Adam Greig, Daniel Richman
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

# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True

"""
Fast Elevation Dataset storage

Note that this module is compiled with Cython to enable fast
memory access.
"""

import sys
import os
import os.path
import mmap

from magicmemoryview import MagicMemoryView

from libc.math cimport round


# In this module, everything is indexed [row][col] (or, [lat][lon]).

cdef resolution = 240

cdef size_t block_rows = 10800
cdef size_t block_cols = 14400

shape = (4, 6, 10801, 14401)


cdef class Dataset:
    cdef short[:, :, :, :] data

    def __init__(self, filename="/opt/elevation"):
        prot = mmap.PROT_READ
        flags = mmap.MAP_SHARED

        with open(filename) as f:
            m = mmap.mmap(f.fileno(), length=0, prot=prot, flags=flags)
            self.data = MagicMemoryView(m, shape, b'h')

    cdef short get_cell(self, int row, int col):
        cdef int block_r, block_c

        print("Get", row, col)
        block_r = row / block_rows
        row %= block_rows
        block_c = col / block_cols
        col %= block_cols
        print("Get", block_r, block_c, row, col)

        return self.data[block_r, block_c, row, col]

    def get(self, double lat, double lng):
        if not -90 <= lat <= 90:
            raise ValueError("Bad latitude {0}".format(lat))
        if not 0 <= lng < 360:
            raise ValueError("Bad longitude {0}".format(lng))

        cdef double i_f, j_f

        i_f = 90 - lat
        j_f = (lng + 180) % 360

        cdef int i, j

        i = <int> round(i_f * resolution)
        j = <int> round(j_f * resolution)

        return self.get_cell(i, j)
