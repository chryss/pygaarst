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

*Created by Chris Waigl on 2013-09-18.*
"""

from __future__ import division, print_function
import os, os.path
import numpy as np
import datetime

import logging
logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger('pygaarst.raster')

from osgeo import gdal, osr
try:
    from pyproj import Proj
except ImportError:
    LOGGER.warning("PROJ4 is not available. Any method requiring coordinate transform will fail.")
# from netCDF4 import Dataset as netCDF
try:
    import h5py
except ImportError:
    LOGGER.warning("The h5py library couldn't be imported, so HDF5 files aren't supported")

import pygaarst.landsatutils as lu
import pygaarst.mtlutils as mtl
import pygaarst.hyperionutils as hyp
import pygaarst.irutils as ir

# GDAL doesn't by default use exceptions
gdal.UseExceptions()

# custom exception
class PygaarstRasterError(Exception):
    """Custom exception for errors during raster processing in Pygaarst"""
    pass

# helper function
def _test_outside(testx, lower, upper):
    """
    True if testx, or any element of it is outside [lower, upper].
    
    Both lower bound and upper bound included 
    Input: Integer or floating point scalar or Numpy array. 
    """
    test = np.array(testx)
    return np.any(test < lower) or np.any(test > upper)

class GeoTIFF(object):
    """
    Represents a GeoTIFF file for data access and processing and provides
    a number of useful methods and attributes.
    
    Arguments:
      filepath (str): the full or relative file path
    """
    def __init__(self, filepath):
        try:
            self.dataobj = gdal.Open(filepath)
        except RuntimeError as e:
            LOGGER.error("Could not open %s: %s" % (filepath, e.message))
            raise
        self.filepath = filepath
        self.ncol = self.dataobj.RasterXSize
        self.nrow = self.dataobj.RasterYSize
        self.nbands = self.dataobj.RasterCount
        self._gtr = self.dataobj.GetGeoTransform()
        # see http://www.gdal.org/gdal_datamodel.html
        self.ulx = self._gtr[0]
        self.uly = self._gtr[3]
        self.lrx = self.ulx + self.ncol * self._gtr[1] + self.nrow * self._gtr[2]
        self.lry = self.uly + self.ncol * self._gtr[4] + self.nrow * self._gtr[5]
        if self._gtr[2] != 0 or self._gtr[4] != 0:
            LOGGER.warning("The dataset is not north-up. The geotransform is given by: (%s). Northing and easting values will not have expected meaning." % ', '.join([str(item) for item in nsdic._gtr]))
        self.dataobj = None
    
    @property
    def data(self):
        """2D numpy array for single-band GeoTIFF file data. Otherwise, 3D. """
        if not self.dataobj:
            self.dataobj = gdal.Open(self.filepath)
        dat = self.dataobj.ReadAsArray()
        self.dataobj = None
        return dat
    
    @property
    def projection(self):
        """The dataset's coordinate reference system as a Well-Known String (WKT)"""
        if not self.dataobj:
            self.dataobj = gdal.Open(self.filepath)        
        dat = self.dataobj.GetProjection()
        self.dataobj = None
        return dat        
    
    @property
    def proj4(self):
        """The dataset's coordinate reference system as a PROJ4 string"""
        osrref = osr.SpatialReference()
        osrref.ImportFromWkt(self.projection)
        return osrref.ExportToProj4()
    
    @property
    def coordtrans(self):
        """A PROJ4 Proj object, which is able to perform coordinate
        transformations"""
        return Proj(self.proj4)
    
    @property
    def delx(self):
        """The sampling distance in x-direction, in physical units (eg metres)"""
        return self._gtr[1]
    
    @property
    def dely(self):
        """The sampling distance in y-direction, in physical units (eg metres)"""
        return self._gtr[5]
    
    @property
    def easting(self): 
        """The x-coordinates of first row pixel corners, 
        as a numpy array: upper-left corner of upper-left pixel 
        to upper-right corner of upper-right pixel (ncol+1)."""
        return np.arange(self.ulx, self.lrx + self.delx, self.delx)
    
    @property
    def northing(self): 
        """The y-coordinates of first column pixel corners, 
        as a numpy array: upper-left corner of upper-left pixel to 
        lower-left corner of lower-left pixel (ncol+1)."""
        return np.arange(self.lry, self.uly - self.dely, -self.dely)
    
    @property
    def x_pxcenter(self): 
        """The x-coordinates of pixel centers, as a numpy array ncol."""
        return np.arange(self.ulx + self.delx/2, self.lrx + self.delx/2, self.delx)
    
    @property
    def y_pxcenter(self): 
        """y-coordinates of pixel centers, nrow."""
        return np.arange(self.lry - self.dely/2, self.uly - self.dely/2, -self.dely)
    
    @property
    def _XY(self):
        return np.meshgrid(self.easting, self.northing)
    
    @property
    def _XY_pxcenter(self):
        return np.meshgrid(self.x_pxcenter, self.y_pxcenter)
    
    @property
    def _LonLat_pxcorner(self):
        return self.coordtrans(*self._XY, inverse=True)
    
    @property
    def _LonLat_pxcenter(self):
        return self.coordtrans(*self._XY_pxcenter, inverse=True)
    
    @property
    def Lon(self):
        """Longitude coordinate of each pixel corner, as an array"""
        return self._LonLat_pxcorner[0]
    
    @property
    def Lat(self):
        """Latitude coordinate of each pixel corner, as an array"""
        return self._LonLat_pxcorner[1]
    
    @property
    def Lon_pxcenter(self):
        """Longitude coordinate of each pixel center, as an array"""
        return self._LonLat_pxcenter[0]
    
    @property
    def Lat_pxcenter(self):
        """Latitude coordinate of each pixel center, as an array"""
        return self._LonLat_pxcenter[1]
    
    def ij2xy(self, i, j):
        """
        Converts array index pair(s) to easting/northing coordinate pairs(s).
        
        NOTE: array coordinate origin is in the top left corner whereas 
        easting/northing origin is in the bottom left corner. Easting and
        northing are floating point numbers, and refer to the top-left corner 
        coordinate of the pixel. i runs from 0 to nrow-1, j from 0 to ncol-1.
        For i=nrow and j=ncol, the bottom-right corner coordinate of the
        bottom-right pixel will be returned. This is identical to the bottom-
        right corner.
        
        Arguments: 
            i (int): scalar or array of row coordinate index
            j (int): scalar or array of column coordinate index
            
        Returns:
            x (float): scalar or array of easting coordinates
            y (float): scalar or array of northing coordinates
        """
        if _test_outside(i, 0, self.nrow) or _test_outside(j, 0, self.ncol):
            raise PygaarstRasterError(
                "Coordinates %d, %d out of bounds" % (i, j))
        x = self.easting[0] + j * self.delx
        y = self.northing[-1] + i * self.dely
        return x, y
    
    def xy2ij(self, x, y, precise=False):
        """
        Convert easting/northing coordinate pair(s) to array coordinate 
        pairs(s).
        
        NOTE: see note at ij2xy()

        Arguments:
            x (float): scalar or array of easting coordinates
            y (float): scalar or array of northing coordinates
            precise (bool): if true, return fractional array coordinates
            
        Returns:
            i (int, or float): scalar or array of row coordinate index
            j (int, or float): scalar or array of column coordinate index    
        """
        if ( _test_outside(x, self.easting[0], self.easting[-1]) or
             _test_outside(y, self.northing[0], self.northing[-1])):
            raise PygaarstRasterError("Coordinates out of bounds")
        i = (1 - (y  - self.northing[0])/(self.northing[-1] - 
            self.northing[0])) * self.nrow
        j = (x - self.easting[0])/(self.easting[-1] - 
            self.easting[0]) * self.ncol
        if precise:
            return i, j
        else:
            return int(np.floor(i)), int(np.floor(j))
    
    def simpleplot(self):
        """Quick and dirty plot of each band (channel, dataset) in the image.
        Requires Matplotlib."""
        import matplotlib.pyplot as plt
        numbands = self.dataobj.RasterCount
        if numbands == 1:
            fig = plt.figure(figsize=(15, 10))
            plt.imshow(self.data[:, :], cmap='bone')
        elif numbands > 1:
            for idx in range(numbands):
                fig = plt.figure(figsize=(15, 10))
                plt.imshow(self.data[idx, :, :], cmap='bone')
    
    def clone(self, newpath, newdata):
        """
        Creates new GeoTIFF object from an existing one: new data, same georeference.
        
        Arguments:
            newpath: valid file path
            newdata: numpy array, 2 or 3-dim
            
        Returns:
            A raster.GeoTIFF object
        """
        # convert Numpy dtype objects to GDAL type codes
        # see https://gist.github.com/chryss/8366492
        
        NPDTYPE2GDALTYPECODE = {
          "uint8": 1, 
          "int8": 1, 
          "uint16": 2, 
          "int16": 3, 
          "uint32": 4, 
          "int32": 5, 
          "float32": 6,
          "float64": 7, 
          "complex64": 10, 
          "complex128": 11, 
        }
        # check if newpath is potentially a valid file path to save data
        dirname, fname = os.path.split(newpath)
        if dirname:
            if not os.path.isdir(dirname):
                raise PygaarstRasterError("%s is not a valid directory to save file to " % dirname)
        if os.path.isdir(newpath):
            LOGGER.warning("%s is a directory. Choose a name that is suitable to writing a dataset to.")
        if newdata.shape != self.data.shape and newdata.shape != self.data[0,...].shape:
            raise PygaarstRasterError("New and cloned GeoTIFF dataset must be the same shape.")
        dims = newdata.ndim
        if dims == 2:
            bands = 1
        elif dims > 2:
            bands = newdata.shape[0]
        else:
            raise PygaarstRasterError("New data array has only %s dimensions." % dims)
        try:
            LOGGER.info(newdata.dtype.name)
            LOGGER.info(NPDTYPE2GDALTYPECODE)
            LOGGER.info(NPDTYPE2GDALTYPECODE[newdata.dtype.name])
            gdaltype = NPDTYPE2GDALTYPECODE[newdata.dtype.name]
        except KeyError as err:
            raise PygaarstRasterError("Data type in array %s cannot be converted to GDAL data type: \n%s" % (newdata.dtype.name, err.message))
        proj = self.projection
        geotrans = self._gtr
        gtiffdr = gdal.GetDriverByName('GTiff')
        gtiff = gtiffdr.Create(newpath, self.ncol, self.nrow, bands, gdaltype)
        gtiff.SetProjection(proj)
        gtiff.SetGeoTransform(geotrans)
        if dims == 2:
            gtiff.GetRasterBand(1).WriteArray(newdata)
        else:
            for idx in range(dims):
                gtiff.GetRasterBand(idx+1).WriteArray(newdata[idx, :, :])
        gtiff = None
        return GeoTIFF(newpath)

# helper function
def _get_spacecraftid(spid):
    """
    Normalizes Landsat SPACECRAFT_ID fields 'Landsat_8' -> 'L8', 'Landsat5' -> 'L5' etc
    """
    if spid.upper().startswith("LANDSAT"):
        return spid[0].upper() + spid[-1]
    else:
        return spid
        
def _validate_platformorigin(platform, spid, sensorid=None):
    """Helper function to validate the correct class for the data was called"""
    if (platform.lower() == 'landsat'):
        if spid not in lu.LANDSATBANDS:
            LOGGER.warning("%s class was used to load data with unrecognized platform ID: %s." % (platform, spid))
    elif (spid == 'EO1' and platform != sensorid):
        LOGGER.warning("%s class was used for data from sensor %s." % (platform, sensorid))

class USGSL1scene(object):
    """
    A container object for multi- and hyperspectral satellite imagery scenes as provided
    as Level 1 (at-sensor calibrated scaled radiance data) by various USGS data portals: 
    Landsat 4/5 TM, Landsat 7 ETM+, Landsat 7 OLI/TIRS, EO1 ALI and EO1 Hyperion
    
    Arguments: 
        dirname (str): name of directory that contains all scene files.
    """
    def __init__(self, dirname):
        self.dirname = dirname
        self.infix = ''
        metadata = mtl.parsemeta(dirname)
        self.meta = metadata['L1_METADATA_FILE']
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
            LOGGER.critical("Error accessing bands %s and %s to calculate NBR." % (label1, label2))
            raise

class Landsatscene(USGSL1scene):
    """
    A container object for TM/ETM+ L5/7 and OLI/TIRS L8 scenes. Input: directory name,
    which is expected to contain all scene files.
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
        self.permissiblebands = lu.get_bands(self.spacecraft)
        _validate_platformorigin('Landsat', self.spacecraft)
        
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
            LOGGER.critical("Error accessing bands %s and %s to calculate NDVI." % (label1, label2))
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
            LOGGER.critical("Error accessing bands %s and %s to calculate NBR." % (label1, label2))
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
        if self.spacecraft == 'L8':
            return lu.naivethermal(self.band10)
        elif self.spacecraft == 'L7':
            return lu.naivethermal(self.band6H)
        else:
            return lu.naivethermal(self.band6)

class Hyperionscene(USGSL1scene):
    """
    A container object for EO-1 Hyperion scenes. Input: directory name,
    which is expected to contain all scene files.
    """
    def __init__(self, dirname):
        super(Hyperionscene, self).__init__(dirname)
        self._hyperiondata = hyp.gethyperionbands()
        self.band_is_calibrated = np.logical_not(self._hyperiondata.Not_Calibrated_X == 'X')
        self.bandselection = []
        self.hyperionbands = self._hyperiondata.Hyperion_Band
        self.calibratedbands = self.hyperionbands[self.band_is_calibrated]
        self.hyperionwavelength_nm = self._hyperiondata.Average_Wavelength_nm
        self.calibratedwavelength_nm = self._hyperiondata.Average_Wavelength_nm[self.band_is_calibrated]

        self.permissiblebands = [str(num) for num in range(1, 243)]
        self.calibratedbands = [str(num) for num in range(8, 58) + range(77, 225)]
        _validate_platformorigin('HYPERION', self.spacecraft, self.sensor)
        
    def __getattr__(self, bandname):
        """
        Override _gettattr__() for bandnames of the form bandN with N in the bands 
        permissible for Hyperion (see https://eo1.usgs.gov/sensors/hyperioncoverage).
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
                if band in self.permissiblebands:
                    isband = True
                    if band not in self.calibratedbands:
                        LOGGER.warning('Hyperion band %s is not calibrated.' % band)
                else:
                    raise PygaarstRasterError(
                        "EO-1 Hyperion does not have a band %s. Permissible band labels are between 1 and 242.")
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
    
    def spectrum(self, i_idx, j_idx, 
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
            bd = self.hyperionbands[self.band_is_calibrated]
        elif bands == 'selected':
            bd = self.hyperionbands[bdsel]
            if bd.size == 0 and self.bandselection:
                bd = self.hyperionbands[self.bandselection]
        elif bands == 'all':
            bd = self.hyperionbands
        elif bands == 'high':
            bd = self.hyperionbands[224:]
        elif bands == 'low':
            bd = self.hyperionbands[:7]
        else:
            raise PygaarstRasterError(
                "Unrecognized argument %s for bands in raser.HyperionScene."
            ) 
        for band in bd:
            rd = self.__getattr__(band).radiance
            rads.append(rd[i_idx, j_idx])
        del rd
        return rads

class ALIscene(USGSL1scene):
    """
    A container object for EO-1 ALI scenes. Input: directory name,
    which is expected to contain all scene files.
    """
    
    def __init__(self, dirname):
        super(ALIscene, self).__init__(dirname)
        self.permissiblebands = [str(num) for num in range(1, 11)]
        _validate_platformorigin('ALI', self.spacecraft, self.sensor)
        
    def __getattr__(self, bandname):
        """
        Override _gettattr__() for bandnames of the form bandN with N in the bands 
        permissible for Hyperion (see https://eo1.usgs.gov/sensors/hyperioncoverage).
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
                if band in self.permissiblebands:
                    isband = True
                else:
                    raise PygaarstRasterError(
                        "EO-1 ALI does not have a band %s. Permissible band labels are between 1 and 10.")
        except ValueError:
            pass
        if isband:
            # Note: Landsat 7 has low and high gain bands 6, with different label names
            keyname = "BAND%s_FILE_NAME" % band
            bandfn = self.meta['PRODUCT_METADATA'][keyname]
            base, ext = os.path.splitext(bandfn)
            postprocessfn = base + self.infix + ext
            bandpath = os.path.join(self.dirname, postprocessfn)
            self.bands[band] = Hyperionband(bandpath, band=band, scene=self)
            return self.bands[band]
        else:
            return object.__getattribute__(self, bandname)

class USGSL1band(GeoTIFF):
    """
    Represents a band of a USGSL1scene. This class is intended to be used via chlid classes:
    Landsatband, Hyperionband, ALIband
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
                LOGGER.warning(
                "Could not find metadata for band object. Set it explicitly: " +
                "[bandobject].meta = pygaarst.landsatutils.parsemeta([metadatafile])"
                )
        super(USGSL1band, self).__init__(filepath)

    @property
    def spacecraft(self):
        try:
            return self.scene.spacecraft
        except AttributeError:
            try:
                return self.meta['PRODUCT_METADATA']['SPACECRAFT_ID']
            except AttributeError:
                LOGGER.warning(
                "Spacecraft not set - should be 'L4', 'L5', '7', 'L8' or 'EO1'. Set a metadata file explicitly: " +
                "[bandobject].meta = pygaarst.landsatutils.parsemeta([metadatafile])"
                )

    @property
    def sensor(self):
        try:
            return self.scene.sensor
        except AttributeError:
            try:
                return self.meta['PRODUCT_METADATA']['SENSOR_ID']
            except AttributeError:
                LOGGER.warning('Sensor not set -- please verify metadata')


class Landsatband(USGSL1band):
    """
    Represents a band of a Landsat scene.

    Implemented: TM/ETM+ L5/7 and OLI/TIRS L8, both old and new metadata format
    """
    def __init__(self, filepath, band=None, scene=None):
        super(Landsatband, self).__init__(filepath, band=band, scene=scene)
        _validate_platformorigin('Landsat', self.spacecraft)

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
                LOGGER.warning(
                "Could not find metadata for band object. Set it explicitly:" +
                "[bandobject].meta = pygaarst.landsatutils.parsemeta([metadatafile])"
                )

    @property
    def radiance(self):
        """Radiance in W / um / m^2 / sr derived from digital number and metadata, as numpy array"""
        if not self.meta:
            raise PygaarstRasterError("Impossible to retrieve metadata for band. No radiance calculation possible.")
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
        """Reflectance between 0 and 1 derived from digital number and metadata, as numpy array"""
        if not self.meta:
            raise PygaarstRasterError("Impossible to retrieve metadata for band. No reflectance calculation possible.")
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
        """Radiant (brightness) temperature at the sensor in K, implemented for Landsat thermal infrared bands."""
        if not self.scene:
            raise PygaarstRasterError("Impossible to retrieve metadata for band. No radiance calculation possible.")
        if (  (self.spacecraft == 'L8' and self.band not in ['10', '11'] )  or
              ( self.spacecraft != 'L8' and not self.band.startswith('6') )):
            LOGGER.warning("Automatic brightness Temp not implemented. Cannot calculate temperature. Sorry.")
            return None
        elif self.spacecraft == 'L8':
            self.k1 =  self.meta['TIRS_THERMAL_CONSTANTS']['K1_CONSTANT_BAND_%s' % self.band]
            self.k2 =  self.meta['TIRS_THERMAL_CONSTANTS']['K2_CONSTANT_BAND_%s' % self.band]
        elif self.spacecraft in ['L4', 'L5', 'L7']:
            self.k1, self.k2 = lu.getKconstants(self.spacecraft)
        return ir.rad2kelvin(self.radiance, self.k1, self.k2)

class Hyperionband(USGSL1band):
    """
    Represents a band of an EO-1 Hyperion scene.
    """
    def __init__(self, filepath, band=None, scene=None):
        super(Hyperionband, self).__init__(filepath, band=band, scene=scene)
        _validate_platformorigin('HYPERION', self.spacecraft, self.sensor)
    
    @property
    def radiance(self):
        """Radiance in W / um / m^2 / sr derived from digital number and metadata, as numpy array"""
        if not self.meta:
            raise PygaarstRasterError("Impossible to retrieve metadata for band. No radiance calculation possible.")
        if int(self.band) <= 70:
            rad = self.data / self.meta['RADIANCE_SCALING']['SCALING_FACTOR_VNIR']
        else:
            rad = self.data / self.meta['RADIANCE_SCALING']['SCALING_FACTOR_SWIR']
        return rad.astype('float32')

class ALIband(USGSL1band):
    """
    Represents a band of an EO-1 ALI scene.
    """
    def __init__(self, filepath, band=None, scene=None):
        super(ALIband, self).__init__(filepath, band=band, scene=scene)
        _validate_platformorigin('ALI', self.spacecraft, self.sensor)
    
    @property
    def radiance(self):
        """Radiance in W / um / m^2 / sr derived from digital number and metadata, as numpy array"""
        if not self.meta:
            raise PygaarstRasterError("Impossible to retrieve metadata for band. No radiance calculation possible.")
        self.gain = self.meta['RADIANCE_SCALING']['BAND%s_SCALING_FACTOR' % self.band]
        self.bias = self.meta['RADIANCE_SCALING']['BAND%s_OFFSET' % self.band]
        return ir.dn2rad(self.data, self.gain, self.bias)

class NetCDF(object):
    pass

class HDF5(object):
    """
    A class providing access to a generic HDF5

    Arguments:
        filepath (str): full or relative path to the data file
    """
    def __init__(self, filepath):
        try:
            LOGGER.info("Opening %s" % filepath)
            self.dataobj = h5py.File(filepath, "r")
            self.filepath = filepath
            self.dirname = os.path.dirname(filepath)
        except IOError as e:
            LOGGER.error("Could not open %s: %s" % (filepath, e.message))
            raise
        if not self.dataobj:
            raise PygaarstRasterError(
                "Could not read data from %s as HDF5 file." % filepath
            )

def _getlabel(groupname):
    labelelems = groupname.split('-')
    print(labelelems)
    if labelelems[-1].startswith(u'GEO'):
        return u'GEO'
    else:
        return labelelems[-2]

class VIIRSHDF5(HDF5):
    """
    A class providing access to a VIIRS HDF5 file or dataset
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
            # It could be an aggregated multi-band VIIRS file with embedded georeferences
            return self.GEO 
        else:
            raise PygaarstRasterError(
                "Unable to find georeference information for %s." % self.filepath
            )
        return geodat
    
    @property
    def lats(self):
        """Latitudes as provided by georeference array"""
        return self.geodata['Latitude' ][:]

    @property
    def lons(self):
        """Longitudes as provided by georeference array"""
        return self.geodata['Longitude' ][:]
