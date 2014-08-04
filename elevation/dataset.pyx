# Copyright 2014 (C) Adam Greig, Daniel Richman
#
# This file is part of Tawhiri.
#
# Tawhiri is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Tawhiri is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Tawhiri.  If not, see <http://www.gnu.org/licenses/>.

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
import mmap

from magicmemoryview import MagicMemoryView

from libc.math cimport round


cdef ssize_t resolution = 1201

block_map_shape = (181, 360)
block_shape = (resolution, resolution)
block_format = b"h"

cdef ssize_t block_map_size = 181 * 360 * sizeof(size_t)
cdef ssize_t block_size = resolution * resolution * sizeof(short)
cdef ssize_t blocks_offset = 128 * 4096

assert block_map_size < blocks_offset


cdef int lat_idx(int lat) except -1:
    if not -90 <= lat <= 90:
        raise ValueError("Bad latitude {0}".format(lat))
    return lat + 90

cdef int lng_idx(int lng) except -1:
    if not 0 <= lng < 360:
        raise ValueError("Bad longitude {0}".format(lng))
    return lng

cdef double lat_i(double lat) except -1:
    if not -90 <= lat <= 90:
        raise ValueError("Bad latitude {0}".format(lat))
    return lat + 90

cdef double lng_j(double lng) except -1:
    if not 0 <= lng < 360:
        raise ValueError("Bad longitude {0}".format(lng))
    return lng


cdef class DatasetBase:
    #: The size in bytes of block_map
    cdef size_t size

    #: An array mapping integer lat, lon to the index of the block.
    cdef long long[:, :] block_map

    cdef int set_block_map(self, memmap) except -1:
        self.block_map = MagicMemoryView(memmap, block_map_shape, b"q")
        return 0

cdef class Dataset(DatasetBase):
    #: The shape of blocks
    cdef object shape
    
    #: The data blocks
    cdef short[:, :, :] blocks

    def __init__(self, filename):
        cdef size_t n_blocks = 0
        cdef size_t sz, sz2

        prot = mmap.PROT_READ
        flags = mmap.MAP_SHARED

        with open(filename, "rb") as f:
            f.seek(0, os.SEEK_END)
            sz = f.tell()

            if sz < block_map_size:
                raise ValueError("Dataset too small: need {0} bytes, got {1}"
                                    .format(block_map_size, sz))

            sz2 = sz - blocks_offset
            if sz2 % block_size != 0:
                raise ValueError("Non-integer number of blocks: {0}"
                                    .format(sz2))

            n_blocks = sz2 / block_size
            self.shape = (n_blocks, ) + block_shape

            f.seek(0, os.SEEK_SET)

            bmap = mmap.mmap(f.fileno(), length=block_map_size, offset=0,
                             prot=prot, flags=mmap.MAP_SHARED)
            self.set_block_map(bmap)

            bs = mmap.mmap(f.fileno(), length=0, offset=blocks_offset,
                           prot=prot, flags=mmap.MAP_SHARED)
            self.blocks = MagicMemoryView(bs, self.shape, block_format)

        cdef size_t i, j
        cdef long long b
        for i in range(block_map_shape[0]):
            for j in range(block_map_shape[1]):
                b = self.block_map[i, j]
                if not -1 <= b < n_blocks:
                    raise ValueError("Map references bad block {0}".format(b))

    def get(self, double lat, double lng):
        cdef int i, j, block_i, block_j, block_idx

        i = <int> round(lat_i(lat) * resolution)
        j = <int> round(lng_j(lng) * resolution)

        block_i = i // resolution
        i = resolution - 1 - (i % resolution)
        block_j = j // resolution
        j = j % resolution

        block_idx = self.block_map[block_i, block_j]

        if block_idx != -1:
            return self.blocks[block_idx, i, j]
        else:
            return 0

cdef class DatasetWriter(DatasetBase):
    cdef object file
    cdef size_t n_blocks

    def __init__(self, filename):
        f = self.file = open(filename, "w+b")
        f.seek(blocks_offset - 1, os.SEEK_SET)
        f.write(b"\0")
        f.seek(0, os.SEEK_SET)

        prot = mmap.PROT_READ | mmap.PROT_WRITE
        bmap = mmap.mmap(f.fileno(), length=block_map_size, offset=0,
                         prot=prot, flags=mmap.MAP_SHARED)

        self.set_block_map(bmap)

        f.seek(blocks_offset, os.SEEK_SET)

    def add_square(self, square_location, data):
        cdef int lat, lng
        cdef size_t dlen, i, j
        cdef unsigned char[:, :, :] src
        cdef short[:, :] dst

        lat, lng = square_location

        self.block_map[lat_idx(lat), lng_idx(lng)] = self.n_blocks
        self.n_blocks += 1

        tmp = bytearray(block_size)

        src = MagicMemoryView(data, block_shape + (2, ), b"B")
        dst = MagicMemoryView(tmp, block_shape, block_format)

        for i in range(block_shape[0]):
            for j in range(block_shape[1]):
                dst[i, j] = (src[i, j, 0] << 8) | src[i, j, 1]

        self.file.write(tmp)
