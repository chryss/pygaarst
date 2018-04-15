# coding: utf-8
"""
**pygaarst.ali**

**ALI-specific classes.**

*Refactored out of pygaarst.raster by Chris Waigl on 2014-11-14.*
"""

from __future__ import division, print_function, absolute_import
from builtins import str
from builtins import range
import os.path
import logging

import pygaarst.irutils as ir
from pygaarst.rasterhelpers import PygaarstRasterError
from pygaarst.usgsl1 import USGSL1scene, USGSL1band, _validate_platformorigin

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger('pygaarst.ali')


class ALIscene(USGSL1scene):
    """
    A container object for EO-1 ALI scenes. Input: directory name,
    which is expected to contain all scene files.
    """

    def __init__(self, dirname):
        super(ALIscene, self).__init__(dirname)
        self.permissiblebandid = [str(num) for num in range(1, 11)]
        _validate_platformorigin('ALI', self.spacecraft, self.sensor)

    def __getattr__(self, bandname):
        """
        Override _gettattr__() for bandnames of the form bandN with N in the
        bands permissible for Ali.

        (See https://eo1.usgs.gov/sensors/hyperioncoverage).
        Warn if band is non-calibrated.
        Allows for infixing the filename just before the .TIF extension for
        pre-processed bands.
        """
        # see https://eo1.usgs.gov/sensors/hyperioncoverage
        isband = False
        head, _, tail = bandname.lower().partition('band')
        try:
            band = tail.upper()
            if head == '':
                if band in self.permissiblebandid:
                    isband = True
                else:
                    raise PygaarstRasterError(
                        "EO-1 ALI does not have a band %s. " +
                        "Permissible band labels are between 1 and 10.")
        except ValueError:
            pass
        if isband:
            # Note: Landsat 7 has low and high gain bands 6,
            # with different label names
            keyname = "BAND%s_FILE_NAME" % band
            bandfn = self.meta['PRODUCT_METADATA'][keyname]
            base, ext = os.path.splitext(bandfn)
            postprocessfn = base + self.infix + ext
            bandpath = os.path.join(self.dirname, postprocessfn)
            self.bands[band] = ALIband(bandpath, band=band, scene=self)
            return self.bands[band]
        return object.__getattribute__(self, bandname)


class ALIband(USGSL1band):
    """
    Represents a band of an EO-1 ALI scene.
    """
    def __init__(self, filepath, band=None, scene=None):
        super(ALIband, self).__init__(filepath, band=band, scene=scene)
        _validate_platformorigin('ALI', self.spacecraft, self.sensor)

    @property
    def radiance(self):
        """Radiance in W / um / m^2 / sr derived from digital number
        and metadata, as numpy array"""
        if not self.meta:
            raise PygaarstRasterError(
                "Impossible to retrieve metadata for band. " +
                "No radiance calculation possible.")
        self.gain = self.meta[
            'RADIANCE_SCALING']['BAND%s_SCALING_FACTOR' % self.band]
        self.bias = self.meta['RADIANCE_SCALING']['BAND%s_OFFSET' % self.band]
        return ir.dn2rad(self.data, self.gain, self.bias)
