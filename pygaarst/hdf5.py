# coding: utf-8
"""
**pygaarst.hdf5**

**HDF5-specific classes, including for VIIRS SDS data.**

*Refactored out of pygaarst.raster by Chris Waigl on 2014-11-17.*
"""

from __future__ import division, print_function, absolute_import
import os.path
from xml.dom import minidom

import logging
logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger('pygaarst.hdf5')

import numpy as np
from osgeo import osr
try:
    from pyproj import Proj
except ImportError:
    LOGGER.warning(
        "PROJ4 is not available. "
        "Any method requiring coordinate transform will fail.")
from pygaarst.rasterhelpers import PygaarstRasterError

try:
    import h5py
except ImportError:
    LOGGER.warning(
        "The h5py library couldn't be imported, "
        "so HDF5 files aren't supported")

class HDF5(object):
    """
    A class providing access to a generic HDF5

    Arguments:
        filepath (str): full or relative path to the data file
    """
    def __init__(self, filepath):
        try:
            #LOGGER.info("Opening %s" % filepath)
            self.dataobj = h5py.File(filepath, "r")
            self.filepath = filepath
            self.dirname = os.path.dirname(filepath)
        except IOError as err:
            LOGGER.error("Could not open %s: %s" % (filepath, err.message))
            raise
        if not self.dataobj:
            raise PygaarstRasterError(
                "Could not read data from %s as HDF5 file." % filepath
            )

def _getlabel(groupname):
    """Returns a useful group label for HDF5 datasets from VIIRS"""
    labelelems = groupname.split('-')
    if labelelems[-1].startswith(u'GEO'):
        return u'GEO'
    else:
        return labelelems[-2]

class VIIRSHDF5(HDF5):
    """
    A class providing access to a VIIRS SDS HDF5 file or dataset
    Parameters:
    filepath: full or relative path to the data file
    geofilepath (optional): override georeference array file from
    metadata; full or relative path to georeference file
    variable (optional): name of a variable to access
    """
    def __init__(self, filepath, geofilepath=None, variable=None):
        super(VIIRSHDF5, self).__init__(filepath)
        self.bandnames = self.dataobj['All_Data'].keys()
        self.bandlabels = {_getlabel(nm): nm for nm in self.bandnames}
        self.bands = {}
        self.bandname = self.dataobj['All_Data'].keys()[0]
        self.datasets = self.dataobj['All_Data/'+self.bandname].items()
        if geofilepath:
            self.geofilepath = geofilepath
        else:
            try:
                geofn = self.dataobj.attrs['N_GEO_Ref'][0][0]
                self.geofilepath = os.path.join(self.dirname, geofn)
            except KeyError:
                self.geofilepath = None

    def __getattr__(self, bandname):
        """
        Override _gettattr__() for bandnames in self.bandlabels.
        """
        if bandname in self.bandlabels:
            return self.dataobj['All_Data/' + self.bandlabels[bandname]]
        else:
            return object.__getattribute__(self, bandname)

    @property
    def geodata(self):
        """Object representing the georeference data, in its entirety"""
        if self.geofilepath:
            geodat = h5py.File(self.geofilepath, "r")
            if not geodat:
                raise PygaarstRasterError(
                    "Unable to open georeference file %s." % self.geofilepath
                )
            self.geogroupkey = geodat['All_Data'].keys()[0]
            return geodat['All_Data/%s' % self.geogroupkey]
        elif self.GEO:
            # It could be an aggregated multi-band VIIRS file
            # with embedded georeferences
            return self.GEO
        else:
            raise PygaarstRasterError(
                "Unable to find georeference information for %s."
                % self.filepath)
        return geodat

    @property
    def lats(self):
        """Latitudes as provided by georeference array"""
        return self.geodata['Latitude'][:]

    @property
    def lons(self):
        """Longitudes as provided by georeference array"""
        return self.geodata['Longitude'][:]
