# coding: utf-8
"""
pygaarst.hyperionutils

Utility functions for processing Hyperion datasets

Created by Chris Waigl on 2014-04-25.
"""
import os, os.path
import numpy as np

def gethyperionbands():
    """Load Hyperion spectral band values into Numpy structured array. 
    Source: http://eo1.usgs.gov/sensors/hyperioncoverage"""
    this_dir, this_filename = os.path.split(__file__)
    tabfile = os.path.join(this_dir, 'Hyperion_Spectral_coverage.tab')
    converter = lambda x: x.replace('B', 'band')
    return np.recfromtxt(
        tabfile, 
        delimiter='\t',
        skip_header=1, 
        names=True,
        converters={0: converter}
        )
        
