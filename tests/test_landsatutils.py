#!/usr/bin/env python
# encoding: utf-8
"""
test_landsatutils.py

Created by Chris Waigl on 2013-11-10.
"""

from __future__ import division, print_function, absolute_import
import os, os.path
import pytest
from pygaarst import landsatutils as lu

def setup_module(module):
    global datadir
    datadir = 'tests/data'
    global scname 
    scname = 'LC8_test'

@pytest.fixture(scope='module')
def landsatscene():
    from pygaarst import landsat
    scpath = os.path.join(datadir, scname)
    sc = landsat.Landsatscene(scpath)
    sc.infix = '_clip'
    return sc

def test_getKconst():
    assert lu.getKconstants('L5') == (607.76, 1260.56)

def test_getbands():
    assert lu.get_bands('L8')[3] == '4'

def test_oldnew():
    assert lu.lskeyselect(False, 'DATE_ACQUIRED') == 'ACQUISITION_DATE'

def test_TIRlabel():
    assert  lu.getTIRlabel('L8') == 'band10'

def test_d():
    assert lu.getd(100) == 1.00184

def test_esun():
    assert lu.getesun('L5', '5') == 225.7

def test_tir(landsatscene):
    tir = landsatscene.TIRband
    assert lu.naivethermal(tir)[0][0] == 0.0

def test_LTK(landsatscene):
    assert lu.LTKcloud(landsatscene)[3][3] == 5.0

def test_tKelvin(landsatscene):
    assert landsatscene.band10.tKelvin[-1][7] == 300.38249200364885

def test_metadataformat(landsatscene):
    assert landsatscene.band10.newmetaformat