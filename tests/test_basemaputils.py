#!/usr/bin/env python
# encoding: utf-8
"""
test_basemaputils.py

Created by Chris Waigl on 2013-09-21.
"""

from __future__ import division, print_function, absolute_import
import os, os.path
import pytest
import mpl_toolkits
from pygaarst import basemaputils as maputil


def test_map_creation():
    m = maputil.map_interiorAK(earth='black')
    assert type(m) is mpl_toolkits.basemap.Basemap
    assert m.proj4string == '+lon_0=-150.0 +y_0=600000.0 +R=6370997.0 +proj=aea +x_0=900000.0 +units=m +lat_2=75.0 +lat_1=55.0 +lat_0=65.0 '