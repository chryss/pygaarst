#!/usr/bin/env python
# encoding: utf-8
"""
test_raster.py

Created by Chris Waigl on 2013-09-18.
"""

from __future__ import division, print_function, absolute_import
import os, os.path
import pytest
from pygaarst import raster

DATADIR = "tests/data"

def setup_module(module):
    mydir = DATADIR
    global badgeotiff
    badgeotiff = os.path.join(mydir, 'test.tiff')
    global rgbgeotiff
    rgbgeotiff = os.path.join(mydir, 'LC8_754_8bit.tiff')
    global viirsh5data
    viirsh5data = os.path.join(
        mydir, 
        'testpyM15.h5')

def test_invalid_geotiff_open(capsys):
    with pytest.raises(RuntimeError):
        a = raster.GeoTIFF(badgeotiff)

def test_valid_geotiff_open():
    a = raster.GeoTIFF(rgbgeotiff)
    assert a
    
def test_valid_hdf5_open():
    import h5py
    a = raster.HDF5(viirsh5data)
    assert a