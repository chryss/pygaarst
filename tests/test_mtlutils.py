#!/usr/bin/env python
# encoding: utf-8
"""
test_mtlutils.py

Created by Chris Waigl on 2013-11-10.
"""

from __future__ import division, print_function, absolute_import
import os, os.path
import pytest
from pygaarst import mtlutils as mtl

DATADIR = "tests/data"

def setup_module(module):
    mydir = DATADIR
    metadatapath8 = os.path.join(mydir, "LC8_test", "LC8_test_MTL.txt")
    global metadatapaths
    metadatapaths = [
        metadatapath8, 
#        datapath7, datapath51, datapath52
    ]

def test_file():
    for p in metadatapaths:
        a = os.path.isfile(p)
        assert a

def test_read_metadata_L8():
    meta = mtl.parsemeta(metadatapaths[0])
    assert meta['L1_METADATA_FILE']['PRODUCT_METADATA']['SPACECRAFT_ID']  == 'LANDSAT_8'
    assert meta['L1_METADATA_FILE']['METADATA_FILE_INFO']['PROCESSING_SOFTWARE_VERSION'] == 'LPGS_2.2.2'
