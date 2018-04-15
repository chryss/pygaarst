# coding: utf-8
"""
**pygaarst.raster**

**Classes and methods to handle raster file formats.**
**Implemented**:
    - GeoTIFF
    - Landsatband(GeoTIFF)
    - Landsatscene
    - Hyperionscene
    - Hyperion
    - HDF5
    - VIIRSHDF5(HDF)
**TODO:**
    - HDF4
    - MODISHDF4
    - ASTERHDF4
    - NetCDF

*Created by Chris Waigl on 2013-09-18.*
*Refactored 2014-11-15: moved classes in files of their own.
"""

from __future__ import division, print_function, absolute_import
from builtins import object
import logging
# from netCDF4 import Dataset as netCDF

from pygaarst.geotiff import GeoTIFF
from pygaarst.usgsl1 import USGSL1scene, USGSL1band
from pygaarst.landsat import Landsatscene, Landsatband
from pygaarst.ali import ALIscene, ALIband
from pygaarst.hyperion import Hyperionscene, Hyperionband
from pygaarst.hdf5 import HDF5, VIIRSHDF5
from pygaarst.hdf4 import HDF4, MODSWHDF4

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger('pygaarst.raster')

# to be refactored


class NetCDF(object):
    """Implements NetCDF data format"""
    pass
