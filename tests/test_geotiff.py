#!/usr/bin/env python
# encoding: utf-8
"""
test_geotiff.py

Created by Chris Waigl on 2013-09-18.
"""

from __future__ import division, print_function, absolute_import
import os
import numpy as np
import pytest
from pygaarst import geotiff
from pygaarst.rasterhelpers import PygaarstRasterError

DATADIR = "tests/data"
rgbgeotiff = os.path.join(DATADIR, 'LC8_754_8bit.tiff')


def test_valid_geotiff_open():
    a = geotiff.GeoTIFF(rgbgeotiff)
    assert a.ncol == 15
    assert a.nrow == 15


def test_basic_geotiff_properties():
    a = geotiff.GeoTIFF(rgbgeotiff)
    assert a.lrx == 501105.0
    assert a.coordtrans.srs == u'+proj=utm +zone=6 +datum=WGS84 +units=m +no_defs '
    assert isinstance(a, geotiff.GeoTIFF)
    assert a.data[0][10][5] == 55
    assert a.projection == u'PROJCS["WGS 84 / UTM zone 6N",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-147],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","32606"]]'
    assert a.proj4 == u'+proj=utm +zone=6 +datum=WGS84 +units=m +no_defs '
    assert a.coordtrans(-145, 65) == (594301.0123902344, 7209946.446071797)
    assert a.delx == 30.0
    assert a.dely == -30.0
    assert a.easting[0] == 500655.0
    assert a.northing[0] == 7200285.0
    assert a.x_pxcenter[-1] == 501090.0
    assert a.y_pxcenter[-1] == 7200720.0
    assert np.isclose(a.Lon[0][0], -146.98614807600831)
    assert np.isclose(a.Lon_pxcenter[-1][0], -146.98582879544685)
    assert np.isclose(a.Lat[0][0], 64.926695025329934)
    assert np.isclose(a.Lat_pxcenter[-1][0], 64.930598198154968)


def test_geotiff_methods():
    a = geotiff.GeoTIFF(rgbgeotiff)
    assert a.ij2xy(1, 1) == (500685.0, 7200705.0)
    assert a.xy2ij(500750, 7200725) == (0, 3)


def test_geotiff_error():
    a = geotiff.GeoTIFF(rgbgeotiff)
    with pytest.raises(PygaarstRasterError):
        a.ij2xy(250, 1)


def test_geotiff_plotting():
    a = geotiff.GeoTIFF(rgbgeotiff)
    a.simpleplot()


def test_geotiff_cloning(tmpdir):
    a = geotiff.GeoTIFF(rgbgeotiff)
    fn = tmpdir.mkdir("sub").join("clone.tif")
    b = a.clone(str(fn), a.data)
    assert type(b) == geotiff.GeoTIFF