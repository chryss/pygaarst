# coding: utf-8
"""
pygaarst.geomutils

Utility functions for operations associating geometry objects with rasters.
In its simplest form, presumes shapely objects and numpy 2D arrays.

Created by Chris Waigl on 2014-08-27.
"""

from __future__ import division, print_function, absolute_import
from builtins import range
from builtins import object
import logging
import numpy as np

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger('pygaarst.geomutils')

try:
    from shapely.geometry import Point
except ImportError:
    LOGGER.warning(
        "The shapely library couldn't be imported, so geomutils won't work."
    )

# We want to be able to cache results when looping through the
# points of numpy arrays


class Memoize(object):
    """Memoization class for in-polygon test"""
    def __init__(self, func):
        """Initialize function and cache attribute"""
        self.func = func
        self.cache = set([])

    def __call__(self, *args, **kwargs):
        """To use the object to wrap a function, implement caching,
        with the cache depending only on positional arguments"""
        if args in self.cache:
            return 1
        else:
            value = self.func(*args, **kwargs)
            if value == 1:
                self.cache.add(args)
            return value
        # try:
        #     return self.cache[args]
        # except KeyError:
        #     value = self.f(*args, **kwargs)
        #     if value == 1:
        #         self.cache.add(value)
        #     return value

    def __repr__(self):
        """Return the function's docstring"""
        return self.func.__doc__

    def resetcache(self):
        """Reset the cache to empty."""
        self.cache = set([])


def _getpolybounds(arrayshape, polygon):
    """Returns bounds of shapely polygon or array, as int in pixel"""
    jmin, imin, jmax, imax = polygon.bounds
    imin = int(np.max(polygon.bounds[1], 0))
    jmin = int(np.max(polygon.bounds[0], 0))
    imax = int(np.minimum(polygon.bounds[3], arrayshape[0] - 1))
    jmax = int(np.minimum(polygon.bounds[2], arrayshape[1] - 1))
    return imin, jmin, imax, jmax


def _overlaypoly(arrayshape, poly=None):
    """Returns mask raster, 1 for pixels in polygon, 0 otherwise"""
    mask = np.zeros(arrayshape, dtype=int)
    imin, jmin, imax, jmax = _getpolybounds(arrayshape, poly)
    for i in range(imin, imax + 1):
        for j in range(jmin, jmax + 1):
            mask[i, j] = _isinpoly(i, j, poly=poly)
    return mask


@Memoize
def _isinpoly(i, j, poly=None):
    "Check if point is inside polygon. Shapely objects."
    if poly.contains(Point(j, i)):
        return 1
    return 0


def overlayvectors(twoDarray, polygons):
    """
    Calculates a mask array marking the pixels that are inside the polygon.

    Arguments:
      twoDarray: a 2D numpy array
      polygons: either a shapely multipolygon or a polygon object

    Returns:
      array of same dimensions as twoDarray that has 1 for the points within
      the polygons object and 0 otherwise
    """
#    if type(polygons) == 'shapely.geometry.polygon.Polygon':
#       It's a single polygon, not a Multipolygons object (usual case)
#        polygons = list(polygons)
    mask = np.zeros(twoDarray.shape, dtype=int)
    _isinpoly.resetcache()
    try:
        for poly in polygons:
            # Calculat a mask for the polygon: array with 1 for pts within
            # the polygon, and 0 outside
            polymask = _overlaypoly(twoDarray.shape, poly=poly)
            mask = np.maximum(polymask, mask)
    except TypeError:   # single polygon, not multipolygon
        mask = _overlaypoly(twoDarray.shape, poly=polygons)
#_isinpoly.cache = {}
    return mask
