# coding: utf-8
"""
pygaarst.basemaputils

Utility functions for easy plotting on a matplotlib basemap.

Created by Chris Waigl on 2013-09-21.
"""

from __future__ import division, print_function, absolute_import

import numpy as np
from mpl_toolkits.basemap import Basemap

import logging
logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger('pygaarst.basemaputils')

def map_interiorAK(water='lightskyblue', earth='snow', resolution='i'):
    """
    Albers Equal Area map of interior Alaska, with some overridable presets.
    """
    bmap = Basemap(width=1800000, height=1200000, resolution=resolution, projection='aea', lat_1=55., lat_2=75., lat_0=65., lon_0=-150.)
    bmap.drawcoastlines()
    bmap.drawrivers(color=water)
    bmap.drawcountries()
    bmap.fillcontinents(lake_color=water, color=earth)
    bmap.drawmeridians(np.arange(-180, -50, 10), labels=[0, 0, 1, 0])
    bmap.drawparallels(np.arange(30, 80, 5), labels=[0, 2, 0, 0])
    bmap.drawmapboundary(fill_color=water)
    return bmap