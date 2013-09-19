#!/usr/bin/env python
# encoding: utf-8
"""
test_raster.py

Created by Chris Waigl on 2013-09-18.
"""

import os
import pytest
from pygaarst import raster

geotiffdata = './data/test.tiff'

print os.getcwd()

def test_geotiff_open(capsys):
    a = raster.GeoTIFF(geotiffdata)
    out, err = capsys.readouterr()
    assert out.startswith('ERROR 4:')
