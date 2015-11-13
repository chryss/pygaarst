#!/usr/bin/env python
# encoding: utf-8
"""
test_modapsclient.py

Created by Chris Waigl on 2015-04-21.
"""

from __future__ import division, print_function, absolute_import, unicode_literals
import os, os.path
from xml.dom import minidom
from pygaarst import modapsclient
import pytest
from .modapsdummydata import modapsresponses

def mockedresponse(url, data=None):
    try:
        return modapsresponses[url]
    except KeyError:
        return modapsresponses[invalid]
    
def fakeurl(fakepath):
    return fakepath

@pytest.fixture(scope='module')
def mockmodaps():
    a = modapsclient.ModapsClient()
    a._makeurl = fakeurl
    a._rawresponse = mockedresponse
    return a

def test_modapsclient_patching():
    assert len(modapsresponses.keys()) == 7

def test_modapsclient_creation(mockmodaps):
    assert mockmodaps.headers['User-Agent'] == 'satellite RS data fetcher'

def test_startswithax():
    assert modapsclient._startswithax('xmlns:axlskdjf')

# complete this
#def test_parselistofdicts():
#    b = '<container><prefix:key1>VAL1</prefix:key1></container>'

def test_fileURLs(mockmodaps):
    assert mockmodaps.getFileUrls(1)[0].strip() == 'ftp://ladsweb.nascom.nasa.gov/allData/5/MOD021KM/2004/201/MOD021KM.A2004201.2130.005.2010141190341.hdf'

def test_satelliteInstruments(mockmodaps):
    assert mockmodaps.listSatelliteInstruments() == {
        u'AM1M': u'Terra MODIS',
        u'AMPM': u'Combined Aqua & Terra MODIS',
        u'ANC': u'Ancillary Data',
        u'NPP': u'Suomi NPP VIIRS',
        u'PM1M': u'Aqua MODIS'
    }