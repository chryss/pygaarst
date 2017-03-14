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

def map_interiorAK(
    width=1800000,
    height=1200000,
    water='lightskyblue',
    earth='snow',
    resolution='i'):
    """
    Albers Equal Area map of interior Alaska, with some overridable presets.
    """
    bmap = Basemap(
        width=width,
        height=height,
        resolution=resolution,
        projection='aea',
        lat_1=55., lat_2=75., lat_0=65., lon_0=-150.)
    bmap.drawcoastlines()
    #bmap.drawrivers(color=water)
    bmap.drawcountries()
    bmap.fillcontinents(lake_color=water, color=earth)
    # labels = [left,right,top,bottom]
    bmap.drawmeridians(
        np.arange(-180, 180, 10), labels=[False, False, False, 1])
    bmap.drawparallels(
        np.arange(0, 80, 5), labels=[1, 1, False, False])
    bmap.drawmapboundary(fill_color=water)
    return bmap

def maptransform(mmap, record):
    """Given a Basemap object and a Fiona collection record in geographic
    coordinates, return a new record whose coordinates are transformed into
    the map CRS"""
    lons = [item[0] for item in record['geometry']['coordinates'][0]]
    lats = [item[1] for item in record['geometry']['coordinates'][0]]
    record['geometry']['coordinates'] = [[(x, y)
        for (x, y) in zip(mmap(lons, lats)[0], mmap(lons, lats)[1])]]
    return record
