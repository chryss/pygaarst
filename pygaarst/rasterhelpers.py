#!/usr/bin/env python
# encoding: utf-8
"""
pygaarst.rasterhelpers.py

Helper functions (misc).
Created by Chris Waigl on 2014-05-12.
Copyright (c) 2014 Christine F. Waigl. 
"""

import sys
import os, os.path
import numpy as np
import h5py

try:
    import h5py
except ImportError:
    LOGGER.warning("The h5py library couldn't be imported, so HDF5 files aren't supported")

import logging
logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger('pygaarst.rasterhelpers')

def save_hypspec_to_hdf5(outfn, hypsc, spectra, i_coord, j_coord):
    """
    Save a set of spectra to HDF5
    
    Arguments:
      outfn (str): file path of the HDF5 file. Will overwrite.
      usgssc (USGSscene): The (typically) Hyperion scene from which the
          spectra are loaded. Or similar object with same attributes.
      spectra (float): Nympy array. num coord by num wavelengths
      i_coord (int): pixel row coordinate array
      j_coord (int): pixel column coordinate array
    """
    specs_arr = np.array(spectra)
    with h5py.File(outfn, 'w') as fh:
        rowidx = fh.create_dataset("i_row_idx", data=i_coord)
        colidx = fh.create_dataset("j_col_idx", data=j_coord)
        spec = fh.create_dataset("spectrum", data=spectra)
        bandnames = fh.create_dataset(
            "bandname", 
            data=hypsc.hyperionbands[hypsc.band_is_calibrated]
            )
        bandidx = fh.create_dataset(
            "bandindex", 
            data=np.where(hypsc.band_is_calibrated)[0]
            )
        bandwavelength = fh.create_dataset(
            "bandwavelenght_nm", data=hypsc.calibratedwavelength_nm
            )

class Datacube(object):
    """
    A 3D cube of data saved in a HDF5 file. 
    Leaves data empty to be filled afterwards. 
    
    Arguments:
        fn (str): file path of HDF5 file
        bandnames (seq of str): list/array of band names 
        bandwav (float): array of wavelengths in nm
        easting (float): 1D np array of pixel corner x-coordinates, same
            order as in array (usually, W-E)
        northing (float): 1D np array of pixel corner y-coordinates, same
            order as in array (usually, N-S)
        lon (float): 1D array of pixel center longitudes, optional
        lat (float): 1D array of pixel center latitudes, optional
        proj4 (str): Proj4 string of projection, optional
        rastertype (str): only 'grid' implemented. TODO: 'swath'
        set_fh (bool): toggle if an open filehandle is returned as attribute
    """
    def __init__(self, fn, bandnames, bandwav, 
            easting, northing,
            lon=None, lat=None,
            proj4=None, rastertype='grid',            
            set_fh=False):
        self.filepath = fn
        self.bandnames = bandnames
        self.wavelengths = bandwav
        self.easting = easting 
        self.northing = northing
        self.lon = lon
        self.lat = lat
        self.proj4 = proj4
        nbands = len(bandnames)
        # number of x and y pixels the same pixel corner coords
        # that is, we don't have the bottom-right (usually) coordinate,
        # only the top-left coordinate of the bottom-right pixel
        nx = len(easting)
        ny = len(northing)
        with h5py.File(fn, 'w') as fh:
            fh.create_dataset(
                'bandnames', data=bandnames)
            fh.create_dataset(
                'easting', data=easting, dtype=np.float32)
            fh.create_dataset(
                'northing', data=northing, dtype=np.float32)
            fh.create_dataset(
                'data', (nx, ny, nbands))
            if lon:
                fh.create_dataset('lon', data=lon, dtype=np.float32)
            if lat:
                fh.create_dataset('lat', data=lat, dtype=np.float32)
            if proj4:
                fh['data'].attrs['proj4'] = proj4
            fh['data'].attrs['rastertype'] = rastertype
            fh['data'].attrs['bandnames'] = bandnames
            fh['data'].attrs['wavelengths'] = bandwav.astype(np.float32)
        if set_fh:
            self.fh = h5py.File(fn, 'r+')

def main():
    pass


if __name__ == '__main__':
    main()

