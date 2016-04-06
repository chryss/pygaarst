#!/usr/bin/env python
# encoding: utf-8
"""
test_landsat.py

Created by Chris Waigl on 2015-04-22.
"""

from __future__ import division, print_function, absolute_import
import os, os.path
import pytest
from pygaarst import raster
from pygaarst import landsat as ls

def setup_module(module):
    global datadir
    datadir = 'tests/data'
    global scname 
    scname = 'LC8_test'

@pytest.fixture(scope='module')
def landsatscene():
    scpath = os.path.join(datadir, scname)
    sc = raster.Landsatscene(scpath)
    sc.infix = '_clip'
    return sc

@pytest.fixture(scope='module')
def landsatscene_direct():
    scpath = os.path.join(datadir, scname)
    sc = ls.Landsatscene(scpath)
    sc.infix = '_clip'
    return sc

@pytest.fixture(scope='module')
def tirband(landsatscene):
    return landsatscene.TIRband

def test_open_valid_landsatscene(landsatscene):
    assert landsatscene
    assert landsatscene.spacecraft == 'L8'

def test_open_valid_landsatscene_directly(landsatscene_direct):
    assert landsatscene_direct

def test_landsatscene_basic_properties(landsatscene):
    assert int(landsatscene.NDVI[6][6]*100) == 35
    assert int(landsatscene.NBR[6][10]*100) == 27

def test_usgsband_basic_properties(landsatscene):
    assert landsatscene.band2.sensor == 'OLI_TIRS'
    assert landsatscene.band2.spacecraft  == 'L8'

def test_tir(tirband):
    assert tirband.data[5][5] == 28786

def test_LTK(landsatscene):
    assert landsatscene.ltkcloud[3][3] == 5.0

def test_naivecloud(landsatscene):
    assert landsatscene.naivecloud[3][3] == 0.0

def test_radiance(landsatscene):
    assert landsatscene.band7.radiance[2][12] == 1.368852

def test_reflectance(landsatscene):
    assert landsatscene.band7.reflectance[2][12] == 0.074893323237735315