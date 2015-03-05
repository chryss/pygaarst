#!/usr/bin/env python
# encoding: utf-8
"""
test_vector.py

Created by Chris Waigl on 2013-10-28.
"""

import os, os.path
import pytest
from osgeo import gdal
from pygaarst import vector

class Shpfile(object):
    """
    A class providing access to an ESRI Shapefile
    Parameters:
    filepath: full or relative path to the data file
    """
    pass