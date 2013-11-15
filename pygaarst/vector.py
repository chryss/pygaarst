#!/usr/bin/env python
# encoding: utf-8
"""
pygaarst.vector

Classes and methods to handle vector file formats.

Created by Chris Waigl on 2013-10-28.
"""

import os, os.path
import numpy as np

from osgeo import gdal, ogr
from osgeo import osr
from pyproj import Proj
from netCDF4 import Dataset as netCDF

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('pygaarst.vector')

# GDAL doesn't by default use exceptions
gdal.UseExceptions()

class Shapefile(object):
    """
    A class providing access to an ESRI Shapefile
    Parameters:
    filepath: full or relative path to the data file
    """
    
    def __init__(self, filepath):
        try:
            logging.info("Opening %s" % filepath)
            self.dataobj = ogr.Open(filepath)
        except RuntimeError as e: 
            logging.error("Could not open %s: %s" % (filepath, e))
            raise
        self.numlayers = self.dataobj.GetLayerCount()
        if self.numlayers == 0:
            logging.error("No layers in shapefile %s" % filepath)
        elif self.numlayers > 1:
            logging.warning("More than one data layer in shapefile %s. Only using the first one." % filepath)
        self.layer = self.dataobj.GetLayer(0)

    @property
    def data(self):
        return [feature for feature in self.layer]
        
    @property
    def proj4(self):
        spref = self.layer.GetSpatialRef()
        return spref.ExportToProj4
    