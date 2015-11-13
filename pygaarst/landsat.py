# coding: utf-8
"""
**pygaarst.landsat**

**Landsat-specific classes.**

*Refactored out of pygaarst.raster by Chris Waigl on 2014-11-14.*
"""

from __future__ import division, print_function, absolute_import
import os.path, datetime
import numpy as np

import logging
logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger('pygaarst.landsat')

import pygaarst.irutils as ir
import pygaarst.landsatutils as lu
from pygaarst.rasterhelpers import PygaarstRasterError
from pygaarst.usgsl1 import USGSL1scene, USGSL1band, _validate_platformorigin

class Landsatscene(USGSL1scene):
    """
    A container object for TM/ETM+ L5/7 and OLI/TIRS L8 scenes

    Arguments:
      dirname (str): the full or relative file path that contains all files
    """
    def __init__(self, dirname):
        super(Landsatscene, self).__init__(dirname)
        # Metadata change, see http://landsat.usgs.gov/Landsat_Metadata_Changes.php
        self.newmetaformat = True
        try:
            versionstr = self.meta['METADATA_FILE_INFO']['PROCESSING_SOFTWARE_VERSION']
        except KeyError:
            versionstr = self.meta['PRODUCT_METADATA']['PROCESSING_SOFTWARE']
            self.newmetaformat = False
        self.permissiblebandid = lu.get_bands(self.spacecraft)
        _validate_platformorigin('Landsat', self.spacecraft)

    def __getattr__(self, bandname):
        """
        Overrides _gettattr__() for bandnames bandN with N in l.LANDSATBANDS.
        Allows for infixing the filename just before the .TIF extension for
        pre-processed bands.
        """
        isband = False
        head, sep, tail = bandname.lower().partition('band')
        try:
            band = tail.upper()
            if head == '':
                if band in self.permissiblebandid:
                    isband = True
                else:
                    raise PygaarstRasterError(
                        "Spacecraft %s " % self.spacecraft
                        + "does not have a band %s. " % band
                        + "Permissible band labels are %s."
                        % ', '.join(self.permissiblebandid))
        except ValueError:
            pass
        if isband:
            # Note: Landsat 7 has low and high gain bands 6,
            # with different label names
            if self.newmetaformat:
                bandstr = band.replace('L', '_VCID_1').replace('H', '_VCID_2')
                keyname = "FILE_NAME_BAND_%s" % bandstr
            else:
                bandstr = band.replace('L', '1').replace('H', '2')
                keyname = "BAND%s_FILE_NAME" % bandstr
            bandfn = self.meta['PRODUCT_METADATA'][keyname]
            base, ext = os.path.splitext(bandfn)
            postprocessfn = base + self.infix + ext
            bandpath = os.path.join(self.dirname, postprocessfn)
            self.bands[band] = Landsatband(bandpath, band=band, scene=self)
            return self.bands[band]
        else:
            return object.__getattribute__(self, bandname)

    @property
    def NDVI(self):
        """The Normalized Difference Vegetation Index"""
        label1, label2 = lu.NDVI_BANDS[self.spacecraft]
        try:
            arr1 = self.__getattr__(label1).data
            arr2 = self.__getattr__(label2).data
            return ir.normdiff(arr1, arr2)
        except AttributeError:
            LOGGER.critical(
                "Error accessing bands %s and %s " % (label1, label2)
                + "to calculate NDVI.")
            raise

    @property
    def NBR(self):
        """The Normalized Burn Index"""
        label1, label2 = lu.NBR_BANDS[self.spacecraft]
        try:
            arr1 = self.__getattr__(label1).data
            arr2 = self.__getattr__(label2).data
            return ir.normdiff(arr1, arr2)
        except AttributeError:
            LOGGER.critical(
                "Error accessing bands %s and %s " % (label1, label2)
                + "to calculate NBR.")
            raise

    @property
    def TIRband(self):
        """Label of a suitable thermal infrared band for the scene.
        Used in loops over Landsat scenes from multiple platform/sensor
        combinations. Will return B6 for L4/5, B6H for L7, B10 for L8."""
        label = lu.getTIRlabel(self.spacecraft)
        return self.__getattr__(label)

    @property
    def ltkcloud(self):
        """Cloud masking and landcover classification with the
        Luo–Trishchenko–Khlopenkov algorithm
        (doi:10.1109/LGRS.2010.2095409).

        Returns:
          A numpy array of the same shape as the input data
          The classes signify:
          - 1.0 - bare ground
          - 2.0 - ice/snow
          - 3.0 - water
          - 4.0 - cloud
          - 5.0 - vegetated soil"""
        return lu.LTKcloud(self)

    @property
    def naivecloud(self):
        """Heuristic cloud masking via thermal IR threshold"""
        if self.spacecraft == 'L8':
            return lu.naivethermal(self.band10)
        elif self.spacecraft == 'L7':
            return lu.naivethermal(self.band6H)
        else:
            return lu.naivethermal(self.band6)

class Landsatband(USGSL1band):
    """
    Represents a band of a Landsat scene.

    Implemented: TM/ETM+ L5/7 and OLI/TIRS L8, old and new metadata format
    """
    def __init__(self, filepath, band=None, scene=None):
        super(Landsatband, self).__init__(filepath, band=band, scene=scene)
        _validate_platformorigin('Landsat', self.spacecraft)

    @property
    def newmetaformat(self):
        """Checks if band uses old or new metadata format"""
        try:
            return self.scene.newmetaformat
        except AttributeError:
            try:
                versionstr = self.meta['METADATA_FILE_INFO']['PROCESSING_SOFTWARE_VERSION']
                return True
            except KeyError:
                versionstr = self.meta['PRODUCT_METADATA']['PROCESSING_SOFTWARE']
                return False
            except AttributeError:
                LOGGER.warning(
                    "Could not find metadata for band object. "
                    + "Set it explicitly: [bandobject].meta = "
                    + "pygaarst.mtlutils.parsemeta([metadatafile])")

    @property
    def radiance(self):
        """
        Radiance in W/um/m^2/sr derived from DN and metadata, as numpy array
        """
        if not self.meta:
            raise PygaarstRasterError(
                "Impossible to retrieve metadata for band. "
                + "No radiance calculation possible.")
        if self.spacecraft == 'L8':
            self.gain = self.meta['RADIOMETRIC_RESCALING']['RADIANCE_MULT_BAND_%s' % self.band]
            self.bias = self.meta['RADIOMETRIC_RESCALING']['RADIANCE_ADD_BAND_%s' % self.band]
            return ir.dn2rad(self.data, self.gain, self.bias)
        elif self.newmetaformat:
            bandstr = self.band.replace('L', '_VCID_1').replace('H', '_VCID_2')
            lmax = self.meta['MIN_MAX_RADIANCE']['RADIANCE_MAXIMUM_BAND_%s' % bandstr]
            lmin = self.meta['MIN_MAX_RADIANCE']['RADIANCE_MINIMUM_BAND_%s' % bandstr]
            qcalmax = self.meta['MIN_MAX_PIXEL_VALUE']['QUANTIZE_CAL_MAX_BAND_%s' % bandstr]
            qcalmin = self.meta['MIN_MAX_PIXEL_VALUE']['QUANTIZE_CAL_MIN_BAND_%s' % bandstr]
            gain, bias = ir.gainbias(lmax, lmin, qcalmax, qcalmin)
            return ir.dn2rad(self.data, gain, bias)
        else:
            bandstr = self.band.replace('L', '1').replace('H', '2')
            lmax = self.meta['MIN_MAX_RADIANCE']['LMAX_BAND%s' % bandstr]
            lmin = self.meta['MIN_MAX_RADIANCE']['LMIN_BAND%s' % bandstr]
            qcalmax = self.meta['MIN_MAX_PIXEL_VALUE']['QCALMAX_BAND%s' % bandstr]
            qcalmin = self.meta['MIN_MAX_PIXEL_VALUE']['QCALMIN_BAND%s' % bandstr]
            gain, bias = ir.gainbias(lmax, lmin, qcalmax, qcalmin)
            return ir.dn2rad(self.data, gain, bias)
        return None

    @property
    def reflectance(self):
        """
        Reflectance (0 .. 1) derived from DN and metadata, as numpy array
        """
        if not self.meta:
            raise PygaarstRasterError(
                "Impossible to retrieve metadata for band. "
                + "No reflectance calculation possible.")
        if self.spacecraft == 'L8':
            self.gain = self.meta['RADIOMETRIC_RESCALING']['REFLECTANCE_MULT_BAND_%s' % self.band]
            self.bias = self.meta['RADIOMETRIC_RESCALING']['REFLECTANCE_ADD_BAND_%s' % self.band]
            sedeg = self.meta['IMAGE_ATTRIBUTES']['SUN_ELEVATION']
            rawrad = ir.dn2rad(self.data, self.gain, self.bias)
            return rawrad/(np.sin(sedeg*np.pi/180))
        elif self.spacecraft in ['L5', 'L7']:
            if self.newmetaformat:
                sedeg = self.meta['IMAGE_ATTRIBUTES']['SUN_ELEVATION']
                dac = self.meta['PRODUCT_METADATA']['DATE_ACQUIRED']
            else:
                sedeg = self.meta['PRODUCT_PARAMETERS']['SUN_ELEVATION']
                dac = self.meta['PRODUCT_METADATA']['ACQUISITION_DATE']
            juliandac = int(datetime.date.strftime(dac, '%j'))
            d = lu.getd(juliandac)
            esun = lu.getesun(self.spacecraft, self.band)
            rad = self.radiance
            return (np.pi * d * d * rad)/(esun * np.sin(sedeg*np.pi/180))
        else:
            return None

    @property
    def tKelvin(self):
        """Radiant (brightness) temperature at the sensor in K,
        implemented for Landsat thermal infrared bands."""
        if not self.scene:
            raise PygaarstRasterError(
                "Impossible to retrieve metadata for band. "
                + "No radiance calculation possible.")
        if ((self.spacecraft == 'L8' and self.band not in ['10', '11'])
                or (self.spacecraft != 'L8' and not self.band.startswith('6'))):
            LOGGER.warning(
                "Automatic brightness Temp not implemented. "
                + "Cannot calculate temperature. Sorry.")
            return None
        elif self.spacecraft == 'L8':
            self.k1 = self.meta['TIRS_THERMAL_CONSTANTS']['K1_CONSTANT_BAND_%s' % self.band]
            self.k2 = self.meta['TIRS_THERMAL_CONSTANTS']['K2_CONSTANT_BAND_%s' % self.band]
        elif self.spacecraft in ['L4', 'L5', 'L7']:
            self.k1, self.k2 = lu.getKconstants(self.spacecraft)
        return ir.rad2kelvin(self.radiance, self.k1, self.k2)
