#!/usr/bin/env python
# encoding: utf-8
"""
test_basemaputils.py

Created by Chris Waigl on 2013-09-21.
"""

from __future__ import division, print_function, absolute_import
import mpl_toolkits
from pygaarst import basemaputils as maputil


def test_map_creation():
    m = maputil.map_interiorAK(earth='black')
    assert type(m) is mpl_toolkits.basemap.Basemap
    assert m.projparams['lat_0'] == 65.0
    assert m.projparams['proj'] == 'aea'
