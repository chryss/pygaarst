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

def main():
    pass


if __name__ == '__main__':
    main()

