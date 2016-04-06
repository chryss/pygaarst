# coding: utf-8
"""
**pygaarst.hdf5**

**HDF4-specific classes, including for HDF-EOS (MODIS) data.**

*Created based on pygaarst.hdf5 by Chris Waigl on 2015-03-05.*
"""

from __future__ import division, print_function, absolute_import
import os.path
import re

import logging
logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger('pygaarst.hdf4')

from osgeo import osr
try:
    from pyproj import Proj
except ImportError:
    LOGGER.warning(
        "PROJ4 is not available. "
        "Any method requiring coordinate transform will fail.")
from pygaarst.rasterhelpers import PygaarstRasterError
import pygaarst.mtlutils as mtl

try:
    import pyhdf.SD
except ImportError:
    LOGGER.warning(
        "The pyhdf library couldn't be imported, "
        "so HDF4 and HDF-EOS files aren't supported")

class HDF4(object):
    """
    A class providing access to a generic HDF4

    Arguments:
        filepath (str): full or relative path to the data file
    """
    def __init__(self, filepath):
        try:
            #LOGGER.info("Opening %s" % filepath)
            self.dataobj = pyhdf.SD.SD(filepath)
            self.filepath = filepath
            self.dirname = os.path.dirname(filepath)
            self.rawmetadata = self.dataobj.attributes()
        except IOError as err:
            LOGGER.error("Could not open %s: %s" % (filepath, err.message))
            raise
        if not self.dataobj:
            raise PygaarstRasterError(
                "Could not read data from %s as HDF4 file." % filepath
            )

class MODSWHDF4(HDF4):
    """
    A class providing access to a MODIS Swath data HDF4-EOS file or dataset
    Currently uses pyhdf (forked) library (required)
    Parameters:
    filepath: full or relative path to the data file
    geofilepath (optional): override georeference array file from
    metadata; full or relative path to georeference file
    variable (optional): name of a variable to access
    """
    def __init__(self, filepath, geofilepath=None, variable=None):
        super(MODSWHDF4, self).__init__(filepath)
        self.datasets = self.dataobj.datasets().keys()
        self.bandnames = None
        self.coremeta = mtl.parsemeta(self.rawmetadata['CoreMetadata.0'])
        self.archivemeta = mtl.parsemeta(self.rawmetadata['ArchiveMetadata.0'])
        self.coremeta = mtl.parsemeta(self.rawmetadata['CoreMetadata.0'])
        if geofilepath:
            self.geofilepath = geofilepath
        else:
            # TODO
            pass

    @property
    def geodata(self):
        """Object representing the georeference data, in its entirety"""
        geodat = None
        if self.geofilepath:
            # TODO
            pass
        else:
            raise PygaarstRasterError(
                "Unable to find georeference information for %s."
                % self.filepath)
        return geodat

    @property
    def lats(self):
        """Latitudes as provided by georeference array"""
        pass

    @property
    def lons(self):
        """Longitudes as provided by georeference array"""
        pass
