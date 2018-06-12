# coding: utf-8
"""
**pygaarst.hdf5**

**HDF5-specific classes, including for VIIRS SDS data.**

*Refactored out of pygaarst.raster by Chris Waigl on 2014-11-17.*
"""

from __future__ import division, print_function, absolute_import
import os.path
import re
import glob
from collections import OrderedDict
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
            self.filepath = filepath
            self.dirname = os.path.dirname(filepath)
            # We'll want, possibly, metadata from the user block, for which
            # the HDF5 obj needs to be closed, but we first need the
            # userblock length. Thus some odd rigamarole...
            self.dataobj = h5py.File(filepath, "r")
            if self.dataobj.userblock_size != 0:
                self.userblock_size = self.dataobj.userblock_size
                self.dataobj.close()
                with open(self.filepath, 'rb') as source:
                    self.userblock = source.read(self.userblock_size)
                self.dataobj = h5py.File(filepath, "r")
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

def _handlenode(node, outdict):
    """Recursive function to parse metadata dictionaries for VIIRS.

    Arguments:
        node: an XML.minidom node
        outdict: the recursively assembled metadata dictionary
    """
    if not node.childNodes:
        outdict[node.nodeName] = None
    elif node.firstChild.nodeType == node.TEXT_NODE:
        outdict[node.nodeName] = node.firstChild.nodeValue
    else:
        newdict = {}
        for childnode in node.childNodes:
            newdict = _handlenode(childnode, newdict)
        try:
            outdict[node.nodeName].append(newdict)
        except KeyError:
            outdict[node.nodeName] = newdict
        except AttributeError:
            outdict[node.nodeName] = [outdict[node.nodeName]]
            outdict[node.nodeName].append(newdict)            
#        print(newdict)
    return outdict

def _latlonmetric(latarray, latref, lonarray, lonref):
    """Takes two numpy arrays of longitudes and latitudes and returns an
    array of the same shape of metrics representing distance for short distances"""
    if latarray.shape != latarray.shape:
        #arrays aren't the same shape
        raise PygaarstRasterError(
            "Latitude and longitude arrays have to be the same shape for " +
            "distance comparisons."
        )
    return np.sqrt(
        np.square(latarray - latref) +
            np.cos(np.radians(latarray)) * np.square(lonarray - lonref))

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
        # put together metadata. First from the userblock, if any:
        self.meta = {}
        if self.userblock:
            self.userblock = self.userblock.rstrip('\x00')
            parsed_ub = minidom.parseString(self.userblock)
            metadatablock = parsed_ub.getElementsByTagName("HDF_UserBlock")
            for node in metadatablock[0].childNodes:
                self.meta = _handlenode(node, self.meta)
        # ... and then from the HDF5 dataobject attributes:
        for key in self.dataobj.attrs:
            self.meta[key] = unicode(self.dataobj.attrs[key][0][0])
        self.bandnames = self.dataobj['All_Data'].keys()
        self.bandlabels = {_getlabel(nm): nm for nm in self.bandnames}
        self.bands = {}
        self.bandname = self.dataobj['All_Data'].keys()[0]
        try:
            self.longbandname = self.meta[u'Data_Product']['N_Collection_Short_Name'] + u'_All'
        except TypeError:
            pass
        self.datasets = self.dataobj['All_Data/'+self.bandname].items()
        if geofilepath:
            self.geofilepath = geofilepath
        else:
            try:
                if not np.shape(self.dataobj.attrs['N_GEO_Ref']):
                    geofn = self.dataobj.attrs['N_GEO_Ref']
                elif (len(np.shape(self.dataobj.attrs['N_GEO_Ref'])) == 1):
                    geofn = self.dataobj.attrs['N_GEO_Ref'][0]
                elif (len(np.shape(self.dataobj.attrs['N_GEO_Ref'])) == 2):
                    geofn = self.dataobj.attrs['N_GEO_Ref'][0][0]
                else:
                    geofn = None
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
            try:
                geodat = h5py.File(self.geofilepath, "r")
            except IOError as err:
                raise PygaarstRasterError(
                    "Unable to open georeference file {}: {}".format(
                        self.geofilepath, err)
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
    def ascending_node(self):
        """True if scene is acquired on an ascending node, otherwise False."""
        middlelatdelta = self.lats[-100, 3199] - self.lats[100, 3199]
        if abs(middlelatdelta) > 500:
            LOGGER.warning(
            "Property 'ascending_node' of {} cannot be easily established. Please assign it manually.".format(
                repr(self)))
            return None
        if middlelatdelta < 0:
            return False
        return True

    @property
    def lats(self):
        """Latitudes as provided by georeference array"""
        return self.geodata['Latitude'][:]

    @property
    def lons(self):
        """Longitudes as provided by georeference array"""
        return self.geodata['Longitude'][:]

    def close(self):
        """Closes open HDF5 file object"""
        self.dataobj.close()
        self.geodata.file.close()

    def getdataset(self, datasetname):
        return self.dataobj['All_Data'][self.longbandname][datasetname][:]

    @property
    def pixelquality(self):
        """Raster of quality factors"""
        return self.getdataset('QF1_VIIRSIBANDSDR')

    def getnearestidx(self, latref, lonref):
        """Returns 2D array index pair that is closest to a given lat/lon point"""
        flatidx = _latlonmetric(self.lats, latref, self.lons, lonref).argmin()
        return np.unravel_index(flatidx, self.lons.shape)

    def crop(self, latref, lonref, delx, dely=None):
        if not dely:
            dely = delx
        """Reduces dataset to +- pixradius pixels around a given location.
        Returns start and end idx in both dimensions for slicing"""
        maxi, maxj = self.lons.shape
        idx = self.getnearestidx(latref, lonref)
        starti = max(0, idx[0] - delx)
        endi = min(idx[0] + delx + 1, maxi)
        startj = max(0, idx[1] - dely)
        endj = min(idx[1] + dely + 1, maxj)
        return starti, endi, startj, endj


def getVIIRSfilesbygranule(basedir, scenelist=[]):
    """
    Returns a dictionary that parses a list of scene directories where each
    name YYYY_MM_DD_JJJ_hhmm refers to an overpass timestamp and contains
    multiple granules and individual desaggregated band files. GINA (the
    Geographic Information Network of Alaska) distributes data this way.
    """
    regex = re.compile(r"(?P<ftype>[A-Z0-9]{5})_[a-z]+_d(?P<date>\d{8})_t(?P<time>\d{7})_e\d+_b(\d+)_c\d+_\w+.h5")
    if scenelist:
        subdirs = filter(
            os.path.isdir,
            [os.path.join(basedir, item) for item in scenelist])
    else:
        subdirs = sorted(glob.glob(
                basedir +
                '/20[0-1][0-9]_[0-1][0-9]_[0-3][0-9]_' +
                '[0-9][0-9][0-9]_[0-2][0-9][0-6][0-9]'))
    overpasses = OrderedDict()
    for subdir in subdirs:
        basename = os.path.split(subdir)[-1]
        overpasses[basename] = {}
        overpasses[basename]['dir'] = os.path.join(subdir, 'sdr')
        datafiles = sorted(
            [item for item in os.listdir(overpasses[basename]['dir'])
                if item.endswith('.h5')])
        if len(datafiles)%25 != 0:
            overpasses[basename]['message'] = "Some data files are missing in {}: {} is not divisible by 25".format(basename, len(datafiles))
        numgran = len(datafiles)//25
        mos = [regex.search(filename) for filename in datafiles]
        for mo, fname in zip(mos, datafiles):
            granulestr = mo.groupdict()['date'] + '_' + mo.groupdict()['time']
            ftype = mo.groupdict()['ftype']
            try:
                overpasses[basename][granulestr][ftype] = fname
            except KeyError:
                overpasses[basename][granulestr] = {}
                overpasses[basename][granulestr][ftype] = fname
    return overpasses
