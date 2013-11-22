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

import landsatutils as lu

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('pygaarst.raster')

# GDAL doesn't by default use exceptions
gdal.UseExceptions()

# custom exception
class PygaarstRasterError(Exception):
    pass

class GeoTIFF(object):
    """
    A class providing access to a GeoTIFF file
    Parameters:
    filepath: full or relative path to the data file
    """
    def __init__(self, filepath):
        try:
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
        numbands = self.dataobj.RasterCount
        if numbands == 1:
            fig = plt.figure(figsize=(15, 10))
            plt.imshow(self.data[:,:], cmap='bone')
        elif numbands > 1:
            for idx in range(numbands):
                fig = plt.figure(figsize=(15, 10))
                plt.imshow(self.data[idx,:,:], cmap='bone')

class Landsatband(GeoTIFF):
    """
    Represents a band of a Landsat scene. 
    
    Implemented: TM/ETM+ L5/7 and OLI/TIRS L8, both old and new metadata format
    """
    def __init__(self, filepath, band=None, scene=None):
        self.band = band
        self.scene = scene
        self.meta = None
        if self.scene:
            self.meta = self.scene.meta
        if not self.meta:
            try:  
                self.meta = lu.parsemeta(os.path.basename(self.filepath))
            except AttributeError: 
                logging.warning(
                "Could not find metadata for band object. Set it explicitly: " + 
                "[bandobject].meta = pygaarst.landsatutils.parsemeta([metadatafile])"
                )
        super(Landsatband, self).__init__(filepath)

    @property
    def spacecraft(self):
        try:
            return self.scene.spacecraft
        except AttributeError:
            try:
                return self.meta['PRODUCT_METADATA']['SPACECRAFT_ID']
            except AttributeError:
                logging.warning(
                "Spacecraft not set - should be 'L4', 'L5', '7', or 'L8'. Set a metadata file explicitly: " + 
                "[bandobject].meta = pygaarst.landsatutils.parsemeta([metadatafile])"
                )

    @property
    def newmetaformat(self):
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
                logging.warning(
                "Could not find metadata for band object. Set it explicitly:" + 
                "[bandobject].meta = pygaarst.landsatutils.parsemeta([metadatafile])"
                )

    @property
    def radiance(self):
        """L8 . Others TBD."""
        if not self.meta:
            raise PygaarstRasterError("Impossible to retrieve metadata for band. No radiance calculation possible.")
        if self.spacecraft == 'L8':
            self.gain = self.meta['RADIOMETRIC_RESCALING']['RADIANCE_MULT_BAND_%s' % self.band]
            self.bias = self.meta['RADIOMETRIC_RESCALING']['RADIANCE_ADD_BAND_%s' % self.band]
            return lu.dn2rad(self.data, self.gain, self.bias)
        elif self.newmetaformat:
            bandstr = self.band.replace('L', '_VCID_1').replace('H', '_VCID_2')
            lmax = self.meta['MIN_MAX_RADIANCE']['RADIANCE_MAXIMUM_BAND_%s' % bandstr]
            lmin = self.meta['MIN_MAX_RADIANCE']['RADIANCE_MINIMUM_BAND_%s' % bandstr]
            qcalmax = self.meta['MIN_MAX_PIXEL_VALUE']['QUANTIZE_CAL_MAX_BAND_%s' % bandstr]
            qcalmin =self.meta['MIN_MAX_PIXEL_VALUE']['QUANTIZE_CAL_MIN_BAND_%s' % bandstr]
            gain, bias = lu.gainbias(lmax, lmin, qcalmax, qcalmin)
            return lu.dn2rad(self.data, gain, bias)
        else:
            bandstr = self.band.replace('L', '1').replace('H', '2')
            lmax = self.meta['MIN_MAX_RADIANCE']['LMAX_BAND%s' % bandstr]
            lmin = self.meta['MIN_MAX_RADIANCE']['LMIN_BAND%s' % bandstr]
            qcalmax = self.meta['MIN_MAX_PIXEL_VALUE']['QCALMAX_BAND%s' % bandstr]
            qcalmin = self.meta['MIN_MAX_PIXEL_VALUE']['QCALMIN_BAND%s' % bandstr]
            gain, bias = lu.gainbias(lmax, lmin, qcalmax, qcalmin)
            return lu.dn2rad(self.data, gain, bias)
#        else:
#            logging.warning("Radiance doesn't seem to be implemented. Check metadata and spacecraft ID attributes. Sorry.")
        return None
        
    @property
    def tKelvin(self):
        """L8 band 10 and 11 only. Others TBD."""
        if not self.scene:
            raise PygaarstRasterError("Impossible to retrieve metadata for band. No radiance calculation possible.")
        if (  (self.spacecraft == 'L8' and self.band not in ['10', '11'] )  or 
              ( self.spacecraft != 'L8' and not self.band.startswith('6') )):
            logging.warning("Automatic brightness Temp not implemented. Cannot calculate temperature. Sorry.")
            return None
        elif self.spacecraft == 'L8':
            self.k1 =  self.meta['TIRS_THERMAL_CONSTANTS']['K1_CONSTANT_BAND_%s' % self.band]
            self.k2 =  self.meta['TIRS_THERMAL_CONSTANTS']['K2_CONSTANT_BAND_%s' % self.band]
        elif self.spacecraft in ['L4', 'L5', 'L7']: 
            self.k1, self.k2 = lu.getKconstants(self.spacecraft)
        return lu.rad2kelvin(self.radiance, self.k1, self.k2)

# helper function
def _get_spacecraftid(spid):
    """
    'Landsat_8' -> 'L8', 'Landsat5' -> 'L5' etc
    """
    return spid[0].upper() + spid[-1]
    
class Landsatscene(object):
    """
    A container object for TM/ETM+ L5/7 and OLI/TIRS L8 scenes. Input: directory name, 
    which is expected to contain all scene files.     
    """

    def __init__(self, dirname):
        self.dirname = dirname
        self.infix = ''
        metadata = lu.parsemeta(dirname)
        self.meta = metadata['L1_METADATA_FILE']
        # first of all, find out software version, metadata format type (new or old)
        # and satellite (L5, L7, L8)
        # Metadata change, see http://landsat.usgs.gov/Landsat_Metadata_Changes.php
        self.newmetaformat = True 
        self.spacecraft = _get_spacecraftid(
            self.meta['PRODUCT_METADATA']['SPACECRAFT_ID']
            )
        try:
            versionstr = self.meta['METADATA_FILE_INFO']['PROCESSING_SOFTWARE_VERSION']
        except KeyError:
            versionstr = self.meta['PRODUCT_METADATA']['PROCESSING_SOFTWARE']
            self.newmetaformat = False
        self.majorswversion = int(versionstr.split('.')[0][5:])
        self.bands = {}
        self.permissiblebands = lu.get_bands(self.spacecraft)
    
    def __getattr__(self, bandname):
        """
        Override _gettattr__() for bandnames of the form bandN with N in l.LANDSATBANDS.
        Allows for infixing the filename just before the .TIF extension for 
        pre-processed bands.
        """
        isband = False
        head, sep, tail = bandname.lower().partition('band')
        try:
            band = tail.upper()
            if head == '':
                if band in self.permissiblebands:
                    isband = True
                else: 
                    raise PygaarstRasterError(
                        "Spacecraft %s does not have a band %s. Permissible band labels are %s." %
                         (self.spacecraft, band, ', '.join(self.permissiblebands)))
        except ValueError:
            pass
        if isband:
            # Note: Landsat 7 has low and high gain bands 6, with different label names
            if self.newmetaformat:
                bandstr = band.replace('L', '_VCID_1').replace('H', '_VCID_2')
                keyname = "FILE_NAME_BAND_%s" % bandstr
            else:
                bandstr = band.replace('L', '1').replace('H', '2')
                keyname = "BAND%s_FILE_NAME" % bandstr
            bandfn = self.meta['PRODUCT_METADATA'][keyname]
            base, ext = os.path.splitext(bandfn)
            postprocessfn = base + self.infix + ext
            bandpath = os.path.join(self.dirname,postprocessfn)
            self.bands[band] = Landsatband(bandpath, band=band, scene=self)
            return self.bands[band]
        else:
            return object.__getattribute__(self, bandname)  

class NetCDF(object):
    pass


class HDF5(object):
    """
    A class providing access to a VIIRS HDF5 file or dataset
    Parameters:
    filepath: full or relative path to the data file
    geofilepath (optional): override georeference array file from
      metadata; full or relative path to georeference file
    variable (optional): name of a variable to access
    TODO: Move VIIRS-specific functionality to VIIRSBand(HDF5).
    """
    import h5py
    def __init__(self, filepath, geofilepath=None, variable=None):
        try:
            logging.info("Opening %s" % filepath)
            self.dataobj = h5py.File(filepath, "r")
            self.filepath = filepath
            self.dirname = os.path.dirname(filepath)
        except IOError as e:
            logging.error("Could not open %s: %s" % (filepath, e))
            raise
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
        
    @property
    def geodataobj(self):
        try:
            geodetics = h5py.File(self.geofilepath, "r")
        except Exception as e:
            print e
        self.geogroupkey = geodetics['All_Data'].keys()[0]
        return geodetics
    
    @property
    def lats(self):
        return self.geodataobj['All_Data/%s/Latitude' % self.geogroupkey][:]

    @property
    def lons(self):
        return self.geodataobj['All_Data/%s/Longitude' % self.geogroupkey][:]
    