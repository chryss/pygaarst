# coding: utf-8
"""
pygaarst.raster

Classes and methods to handle raster file formats.
Implemented:
- GeoTIFF
- HDF5 (stub)
- Landsatband(GeoTIFF)

Created by Chris Waigl on 2013-09-18.
"""

import os, os.path
import numpy as np

import h5py
from osgeo import gdal, osr
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
        self.filepath = filepath
        self.ncol = self.dataobj.RasterXSize
        self.nrow = self.dataobj.RasterYSize
        self._gtr = self.dataobj.GetGeoTransform()
        # see http://www.gdal.org/gdal_datamodel.html
        self.ulx = self._gtr[0]
        self.uly = self._gtr[3]
        self.lrx = self.ulx + self.ncol * self._gtr[1] + self.nrow * self._gtr[2]
        self.lry = self.uly + self.ncol * self._gtr[4] + self.nrow * self._gtr[5]
    
    @property
    def data(self):
        return self.dataobj.ReadAsArray()

    @property
    def projection(self):
        return self.dataobj.GetProjection()

    @property
    def proj4(self):
        osrref = osr.SpatialReference()
        osrref.ImportFromWkt(self.projection)
        return osrref.ExportToProj4()

    def simpleplot(self):
        import matplotlib.pyplot as plt
        numbands = self.data.shape[0]
        for idx in range(numbands):
            fig = plt.figure()
            plt.imshow(self.data[idx,:,:], cmap='bone')


class Landsatscene(object):
    """
    A container object for TM/ETM+ L5/7 and OLI/TIRS L8 scenes. Input: directory name, 
    which is expected to contain all scene files.     
    """
    SPACECRAFTS = {
        'Landsat5': 'L5',
        'LANDSAT_5': 'L5',
        'LANDSAT_7': 'L7',
        'LANDSAT_8': 'L8'
    }
    import landatutils as l
    def __init__(self, dirname):
        try:
            logging.info("Loading Landsat scene %s" % dirname)
        except RuntimeError as e: 
            logging.error("Could not open %s: %s" % (dirname, e))
            raise
        self.location = dirname
        self.meta = l.parsemeta(dirname)
        # first of all, find out software version and satellite 
        

class Landsatband(GeoTIFF):
    """
    Represents a band of a Landsat scene. 
    
    Implemented: v. 11 and 12 of the processing software for TM/ETM+ L5/7 and OLI/TIRS L8
    """
    import landatutils as l
    
    @property
    def meta(self):
        return l.parsemeta(os.path.basename(self.filepath)
    
    
    
class NetCDF(objectc):
    pass


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
        self.geofilepath = geofilepath
        try:
            logging.info("Opening %s" % filepath)
            self.dataobj = h5py.File(filepath, "r")
        except IOError as e:
            logging.error("Could not open %s: %s" % (filepath, e))
            raise
        self.bandname = self.dataobj['All_Data'].keys()[0]
        self.datasets = self.dataobj['All_Data/'+self.bandname].items()
        
    @property
    def geodetics(self):
        try:
            self.geodataobj = h5py.File(self.geofilepath, "r")
        except Exception as e:
            print e
        