#!/usr/bin/env python
# encoding: utf-8
"""
test_hyperion.py

Created by Chris Waigl on 2015-04-22.
"""

from __future__ import division, print_function, absolute_import
import os
import pytest
from pygaarst import hyperion as hyp


def setup_module(module):
    global datadir
    datadir = 'tests/data'
    global scname
    scname = 'LC8_test'


@pytest.fixture(scope='module')
def hyperionscene():
    scpath = os.path.join(datadir, scname)
    sc = hyp.Hyperionscene(scpath)
    sc.infix = '_clip'
    sc.meta['PRODUCT_METADATA']['BAND2_FILE_NAME'] = sc.meta[
        'PRODUCT_METADATA']['FILE_NAME_BAND_2']
    return sc


def test_open_valid_hyperionscene(hyperionscene):
    assert hyperionscene
    assert hyperionscene.spacecraft == 'L8'


def test_hyperion_basic_properties(hyperionscene):
    assert hyperionscene.band2.sensor == 'OLI_TIRS'
    assert hyperionscene.band2.spacecraft == 'L8'


def test_spectrum_invalid(hyperionscene):
    with pytest.raises(KeyError):
        a = hyperionscene.spectrum(0, 0)
        assert a
