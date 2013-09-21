# coding: utf-8
"""
pygaarst.basemaputils

Utility functions for easy plotting on a matplotlib basemap.

Created by Chris Waigl on 2013-09-21.
"""

import os, os.path
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('pygaarst.basemaputils')

def map_interiorAK(water='lightskyblue', earth='snow', resolution='i'):
    """
    Albers Equal Area map of interior Alaska, with some overridable presets. 
    """
    m = Basemap(width=1800000, height=1200000, resolution=resolution, projection='aea', lat_1=55., lat_2=75., lat_0=65., lon_0=-150.)
    m.drawcoastlines()
    m.drawrivers(color=water)
    m.drawcountries()
    m.fillcontinents(lake_color=water, color=earth)
    m.drawmeridians(np.arange(-180, -50, 10), labels=[0, 0, 1, 0])
    m.drawparallels(np.arange(30, 80, 5), labels=[0, 2, 0, 0])
    m.drawmapboundary(fill_color=water)
    return m