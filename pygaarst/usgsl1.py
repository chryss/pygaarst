# coding: utf-8
"""
**pygaarst.geotiff**

**USGSL1 base class, used for Landsat, Hyperion, ALI.**

*Refactored out of pygaarst.raster by Chris Waigl on 2014-11-14.*
"""

from __future__ import division, print_function, absolute_import
from builtins import object
import os.path

import logging
logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger('pygaarst.usgsl1')

import pygaarst.irutils as ir
import pygaarst.landsatutils as lu
import pygaarst.mtlutils as mtl
from pygaarst.geotiff import GeoTIFF
from pygaarst.rasterhelpers import PygaarstRasterError

def _validate_platformorigin(platform, spid, sensorid=None):
    """Helper function to validate the class called for the data was"""
    if platform.lower() == 'landsat':
        if spid not in lu.LANDSATBANDS:
            LOGGER.warning(
                "%s class was used to load data " % platform
                + "with unrecognized platform ID: %s." % spid)
    elif spid == 'EO1' and platform != sensorid:
        LOGGER.warning(
            "%s class was used for data from sensor %s."
            % (platform, sensorid))

# helper function
def _get_spacecraftid(spid):
    """
    Normalizes Landsat SPACECRAFT_ID fields

    'Landsat_8' -> 'L8', 'Landsat5' -> 'L5' etc
    """
    if spid.upper().startswith("LANDSAT"):
        return spid[0].upper() + spid[-1]
    else:
        return spid

class USGSL1scene(object):
    """
    A container object for multi- and hyperspectral satellite imagery scenes
    as provided as Level 1 (at-sensor calibrated scaled radiance data)
    by various USGS data portals: Landsat 4/5 TM, Landsat 7 ETM+,
    Landsat 7 OLI/TIRS, EO1 ALI and EO1 Hyperion

    Arguments:
        dirname (str): name of directory that contains all scene files.
    """
    def __init__(self, dirname):
        self.dirname = dirname
        self.infix = ''
        metadata = mtl.parsemeta(dirname)
        try:
            self.meta = metadata['L1_METADATA_FILE']
        except KeyError:
            raise PygaarstRasterError(
                "Metadata from %s could not be read. " % dirname 
                + " Please check your dataset."
            )
        self.spacecraft = _get_spacecraftid(
            self.meta['PRODUCT_METADATA']['SPACECRAFT_ID']
            )
        self.sensor = self.meta['PRODUCT_METADATA']['SENSOR_ID']
        self.bands = {}

    def get_normdiff(self, label1, label2):
        """Calculate a generic normalized difference index

        Arguments:
          label1, label2 (str): valid band labels, usually of the form 'bandN'
        """
        try:
            arr1 = self.__getattr__(label1).data
            arr2 = self.__getattr__(label2).data
            return ir.normdiff(arr1, arr2)
        except AttributeError:
            LOGGER.critical(
                "Error accessing bands %s and %s to calculate NBR."
                % (label1, label2))
            raise

class USGSL1band(GeoTIFF):
    """
    Represents a band of a USGSL1scene.

    This class is intended to be used via chlid classes: Landsatband,
    Hyperionband, ALIband
    """
    def __init__(self, filepath, band=None, scene=None):
        self.band = band
        self.scene = scene
        self.meta = None
        if self.scene:
            self.meta = self.scene.meta
        if not self.meta:
            try:
                self.meta = mtl.parsemeta(os.path.basename(self.filepath))
            except AttributeError:
                LOGGER.warning(
                    "Could not find metadata for band object. "
                    + "Set it explicitly: [bandobject].meta = "
                    +"pygaarst.mtlutils.parsemeta([metadatafile])"
                )
        super(USGSL1band, self).__init__(filepath)

    @property
    def spacecraft(self):
        """Returns spacecraft name (L4, L5, L7, L8)"""
        try:
            return self.scene.spacecraft
        except AttributeError:
            try:
                return self.meta['PRODUCT_METADATA']['SPACECRAFT_ID']
            except AttributeError:
                LOGGER.warning(
                    "Spacecraft not set - should be 'L4', 'L5', 'L7', "
                    + "'L8' or 'EO1'. Set a metadata file explicitly: "
                    + "[bandobject].meta = "
                    + "pygaarst.mtlutils.parsemeta([metadatafile])"
                )

    @property
    def sensor(self):
        """Returns sensor name"""
        try:
            return self.scene.sensor
        except AttributeError:
            try:
                return self.meta['PRODUCT_METADATA']['SENSOR_ID']
            except AttributeError:
                LOGGER.warning('Sensor not set -- please verify metadata')
