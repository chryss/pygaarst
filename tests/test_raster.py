#!/usr/bin/env python
# encoding: utf-8
"""
test_raster.py

Created by Chris Waigl on 2013-09-18.
"""

import os, os.path
import pytest
from pygaarst import raster

DATADIR = "/Volumes/SCIENCE/Coding/pygaarst/"

def setup_module(module):
    mydir = DATADIR
    global badgeotiff
    badgeotiff = os.path.join(mydir, 'tests/data/test.tiff')
    print badgeotiff
    global rgbgeotiff
    rgbgeotiff = os.path.join(mydir, 'tests/data/LC80680152013194_754_crop2.tiff')
    global viirsh5data
    viirsh5data = os.path.join(
        mydir, 
        'tests/data/SVDNB_npp_d20130725_t2022157_e2023399_b09030_c20130725204748429995_cspp_dev.h5')

def test_invalid_geotiff_open(capsys):
    with pytest.raises(RuntimeError):
        a = raster.GeoTIFF(badgeotiff)

def test_valid_geotiff_open():
    a = raster.GeoTIFF(rgbgeotiff)
    assert a.ncol == 787
    assert a.nrow == 793
    
def test_valid_hdf5_open():
    import h5py
    a = raster.HDF5(viirsh5data)
    assert a.bandname == u'VIIRS-DNB-SDR_All'