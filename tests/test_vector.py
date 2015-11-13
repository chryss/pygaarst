#!/usr/bin/env python
# encoding: utf-8
"""
test_vector.py

Created by Chris Waigl on 2013-10-28.
"""

from __future__ import division, print_function, absolute_import
import os, os.path
import pytest
from pygaarst import vector

DATADIR = "tests/data"
SHP1 = os.path.join(DATADIR, 'shptest.shp')

def test_Shp():
    a = vector.Shapefile(SHP1)
    assert a.proj4 == '+proj=longlat +ellps=WGS84 +no_defs '
    assert a.layer.GetGeomType() == 3