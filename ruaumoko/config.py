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

from os.path import join, dirname

import yaml

def load_config(file_name):
    with open(file_name) as f:
        config = yaml.safe_load(f)

    return config

def default_config():
    file_name = join(dirname(__file__), "default_config.yaml")
    return load_config(file_name)
