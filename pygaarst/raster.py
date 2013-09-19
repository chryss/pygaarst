# coding: utf-8
"""
pygaarst.raster

Classes and methods to handle raster file formats.

Created by Chris Waigl on 2013-09-18.
"""

import os, os.path
import numpy as np
import pylab as plt

from osgeo import gdal, osr
from osgeo import osr
from pyproj import Proj
from netCDF4 import Dataset as netCDF

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('pygaarst.raster')

class GeoTIFF(object):
    """
    A class providing access to a GeoTIFF file
    Parameters:
    filepath: full or relative path to GeoTIFF file
    """
    def __init__(self, filepath):
        try:
            logging.info("Opening %s" % filepath)
            self.fp = gdal.Open(filepath)
        except IOError as e: 
            logging.error("Could not open %s: %s" % (filepath, e))
        
        