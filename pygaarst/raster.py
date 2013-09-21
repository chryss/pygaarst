# coding: utf-8
"""
pygaarst.raster

Classes and methods to handle raster file formats.

Created by Chris Waigl on 2013-09-18.
"""

import os, os.path
import numpy as np

import h5py
from osgeo import gdal, osr
from osgeo import osr
from pyproj import Proj
from netCDF4 import Dataset as netCDF

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('pygaarst.raster')

# GDAL doesn't by default use exceptions
gdal.UseExceptions()

class GeoTIFF(object):
    """
    A class providing access to a GeoTIFF file
    Parameters:
    filepath: full or relative path to the data file
    """
    def __init__(self, filepath):
        try:
            logging.info("Opening %s" % filepath)
            self.dataobj = gdal.Open(filepath)
        except RuntimeError as e: 
            logging.error("Could not open %s: %s" % (filepath, e))
            raise
        self.ncol = self.dataobj.RasterXSize
        self.nrow = self.dataobj.RasterYSize
        
class HDF5(object):
    """
    A class providing access to a HDF file or dataset
    Parameters:
    filepath: full or relative path to the data file
    geofilepath (optional): full or relative path to georeference file
    variable (optional): name of a variable to access
    """
    import h5py
    def __init__(self, filepath, geofilepath=None, variable=None):
        try:
            logging.info("Opening %s" % filepath)
            self.dataobj = h5py.File(filepath, "r")
        except IOError as e:
            logging.error("Could not open %s: %s" % (filepath, e))
            raise
        self.bandname = self.dataobj['All_Data'].keys()[0]
            
        