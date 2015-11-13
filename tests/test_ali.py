#!/usr/bin/env python
# encoding: utf-8
"""
test_ali.py

Created by Chris Waigl on 2015-04-24.
"""

from __future__ import division, print_function, absolute_import
import os, os.path
import pytest
from pygaarst import ali

def setup_module(module):
    global datadir
    datadir = 'tests/data'
    global scname 
    scname = 'LC8_test'

@pytest.fixture(scope='module')
def aliscene():
    scpath = os.path.join(datadir, scname)
    sc = ali.ALIscene(scpath)
    sc.infix = '_clip'
    sc.meta['PRODUCT_METADATA']['BAND2_FILE_NAME'] = sc.meta['PRODUCT_METADATA']['FILE_NAME_BAND_2']
    return sc

def test_open_valid_landsatscene(aliscene):
    assert aliscene
    assert aliscene.spacecraft == 'L8'

def test_ali_basic_properties(aliscene):
    assert aliscene.band2.sensor == 'OLI_TIRS'
    assert aliscene.band2.spacecraft  == 'L8'