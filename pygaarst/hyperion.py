# coding: utf-8
"""
**pygaarst.hyperion**

**Hyperion-specific classes.**

*Refactored out of pygaarst.raster by Chris Waigl on 2014-11-14.*
"""

from __future__ import division, print_function, absolute_import
import os.path
import itertools
import numpy as np

import logging
logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger('pygaarst.hyperion')

import pygaarst.hyperionutils as hyp
import pygaarst.rasterhelpers as rh
from pygaarst.rasterhelpers import PygaarstRasterError
from pygaarst.usgsl1 import USGSL1scene, USGSL1band, _validate_platformorigin

class Hyperionscene(USGSL1scene):
    """
    A container object for EO-1 Hyperion scenes. Input: directory name,
    which is expected to contain all scene files.
    """
    def __init__(self, dirname):
        super(Hyperionscene, self).__init__(dirname)
        self._hyperiondata = hyp.gethyperionbands()
        self.band_is_calibrated = np.logical_not(
            self._hyperiondata.Not_Calibrated_X == 'X')
        self.bandselection = []
        self.hyperionbands = self._hyperiondata.Hyperion_Band
        self.calibratedbands = self.hyperionbands[self.band_is_calibrated]
        self.hyperionwavelength_nm = self._hyperiondata.Average_Wavelength_nm
        self.calibratedwavelength_nm = self._hyperiondata.Average_Wavelength_nm[
            self.band_is_calibrated]
        self.permissiblebandid = [str(num) for num in range(1, 243)]
        self.calibratedbandid = [
            str(num) for num in itertools.chain(range(8, 58), range(77, 225))]
        _validate_platformorigin('HYPERION', self.spacecraft, self.sensor)

    def __getattr__(self, bandname):
        """
        Override _gettattr__() for bandnames bandN with N in the bands
        permissible for Hyperion

        (See https://eo1.usgs.gov/sensors/hyperioncoverage).
        Warn if band is a non-calibrated one.
        Allows for infixing the filename just before the .TIF extension for
        pre-processed bands.
        """
        # see https://eo1.usgs.gov/sensors/hyperioncoverage
        isband = False
        head, sep, tail = bandname.lower().partition('band')
        try:
            band = tail.upper()
            if head == '':
                if band in self.permissiblebandid:
                    isband = True
                    if band not in self.calibratedbandid:
                        LOGGER.warning(
                            'Hyperion band %s is not calibrated.' % band)
                else:
                    raise PygaarstRasterError(
                        "EO-1 Hyperion does not have a band %s. "  % band
                        + "Permissible band labels are between 1 and 242.")
        except ValueError:
            pass
        if isband:
            keyname = "BAND%s_FILE_NAME" % band
            bandfn = self.meta['PRODUCT_METADATA'][keyname]
            base, ext = os.path.splitext(bandfn)
            postprocessfn = base + self.infix + ext
            bandpath = os.path.join(self.dirname, postprocessfn)
            self.bands[band] = Hyperionband(bandpath, band=band, scene=self)
            return self.bands[band]
        else:
            return object.__getattribute__(self, bandname)

    def spectrum(
            self, i_idx, j_idx,
            bands='calibrated',
            bdsel=[]):
        """
        Calculates the radiance spectrum for one pixel.

        Arguments:
          i_idx (int): first coordinate index of the pixel
          j_idx (int): second coordinate index of the pixel
          bands (str): indicates the bands that are used
            'calibrated' (default): only use calibrated bands
            'high': use uncalibrated bands 225-242
            'low': use uncalibrated bands 1-7
            'all': use all available bands
            'selected': use bdsel attribute or argument
          bdsel: sequence data type containing band indices to select
        """
        rads = []
        if bands == 'calibrated':
            bnd = self.hyperionbands[self.band_is_calibrated]
        elif bands == 'selected':
            bnd = self.hyperionbands[bdsel]
            if bnd.size == 0 and self.bandselection:
                bnd = self.hyperionbands[self.bandselection]
        elif bands == 'all':
            bnd = self.hyperionbands
        elif bands == 'high':
            bnd = self.hyperionbands[224:]
        elif bands == 'low':
            bnd = self.hyperionbands[:7]
        else:
            raise PygaarstRasterError(
                "Unrecognized argument %s for bands " % bands
                + "in raser.HyperionScene.")
        for band in bnd:
            rad = self.__getattr__(band).radiance
            rads.append(rad[i_idx, j_idx])
        del rad
        return rads

    def get_datacube(
            self, outfn,
            bandlist, islice=None, jslice=None,
            set_fh=False):
        """
        Creates a rasterhelpers.Datacube object from a bandlist and the
        radiance data from the whole Hyperion scene.

        Arguments:
            outfn (str): file path of the HDF5 file that stores the cube
            bandlist (sequence of str): a list or array of band names
            islice (sequence of int): list or array of row indices
            jslice (sequence of int): list or array of column indices
            set_fh (bool): should an open filehandle be set as an argument?
        """
        if len(bandlist) == 0:
            return None
        sampleband = self.__getattr__(bandlist[0])
        if not islice:
            islice = list(range(sampleband.nrow))
        if not jslice:
            jslice = list(range(sampleband.ncol))
        revnorth = sampleband.northing[::-1]
        east = sampleband.easting[...]
        scenecube = rh.Datacube(
            outfn,
            self.calibratedbands,
            self.calibratedwavelength_nm,
            east[jslice],
            revnorth[islice],
            proj4=sampleband.proj4,
            set_fh=True
        )
        for bidx, band in enumerate(bandlist):
            banddata = self.__getattr__(band).radiance
            scenecube.fh['data'][:, :, bidx] = banddata[
                np.meshgrid(islice, jslice)]
        if not set_fh:
            scenecube.fh.close()
        return scenecube

class Hyperionband(USGSL1band):
    """
    Represents a band of an EO-1 Hyperion scene.
    """
    def __init__(self, filepath, band=None, scene=None):
        super(Hyperionband, self).__init__(filepath, band=band, scene=scene)
        _validate_platformorigin('HYPERION', self.spacecraft, self.sensor)

    @property
    def radiance(self):
        """Radiance in W / um / m^2 / sr derived from digital number and
        metadata, as numpy array"""
        if not self.meta:
            raise PygaarstRasterError(
                "Impossible to retrieve metadata "
                + "for band. No radiance calculation possible.")
        if int(self.band) <= 70:
            rad = self.data / self.meta['RADIANCE_SCALING']['SCALING_FACTOR_VNIR']
        else:
            rad = self.data / self.meta['RADIANCE_SCALING']['SCALING_FACTOR_SWIR']
        return rad.astype('float32')
