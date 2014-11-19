#!/usr/bin/env python
# encoding: utf-8
"""
test_raster.py

Created by Chris Waigl on 2013-11-10.
"""

import os, os.path
import pytest
from pygaarst import mtlutils as mtl

def setup_module(module):
    mydir = os.getcwd()
    datapath8 = os.path.join(mydir, "tests/data/LC80690152013153LGN00_MTL.txt")
    datapath51 = os.path.join(mydir, "tests/data/LT50690152011132GLC00_MTL.txt")
    datapath52 = os.path.join(mydir, "tests/data/L5070015_01520090716_MTL.txt")
    datapath7 = os.path.join(mydir, "tests/data/LE70700152011147EDC00_MTL.txt")
    global datapaths
    datapaths = [datapath8, datapath7, datapath51, datapath52]

def test_file():
    for p in datapaths:
        a = os.path.isfile(p)
        assert a

def test_read_metadata_L8():
    meta = mtl.parsemeta(datapaths[0])
    assert meta['L1_METADATA_FILE']['PRODUCT_METADATA']['SPACECRAFT_ID']  == 'LANDSAT_8'
    assert meta['L1_METADATA_FILE']['METADATA_FILE_INFO']['PROCESSING_SOFTWARE_VERSION'] == 'LPGS_2.2.2'


def test_read_metadata_L7():
    meta = mtl.parsemeta(datapaths[1])
    assert meta['L1_METADATA_FILE']['PRODUCT_METADATA']['SPACECRAFT_ID']  == 'LANDSAT_7'
    assert meta['L1_METADATA_FILE']['METADATA_FILE_INFO']['PROCESSING_SOFTWARE_VERSION'] == 'LPGS_12.2.1'

def test_read_metadata_L51():
    meta = mtl.parsemeta(datapaths[2])
    assert meta['L1_METADATA_FILE']['PRODUCT_METADATA']['SPACECRAFT_ID']  == 'LANDSAT_5'
    assert meta['L1_METADATA_FILE']['METADATA_FILE_INFO']['PROCESSING_SOFTWARE_VERSION'] == 'LPGS_12.2.1'

def test_read_metadata_L52():
    meta = mtl.parsemeta(datapaths[3])
    assert meta['L1_METADATA_FILE']['PRODUCT_METADATA']['SPACECRAFT_ID']  == 'Landsat5'
    assert meta['L1_METADATA_FILE']['PRODUCT_METADATA']['PROCESSING_SOFTWARE'] == 'LPGS_11.5.1'

