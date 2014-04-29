***********************************
Working with generic raster formats
***********************************

GeoTIFF
=======
Pygaarst :mod:`raster` module provides a custom :py:class:`GeoTIFF` class
with methods and properties that aim at making it easy to open and process
GeoTIFF files. It works with both single and multi-band GeoTIFF files. Under 
the hood, the GeoTIFF class uses GDAL, so the instance attributes it makes
available are will look familiar to those who work with GDAL. The default 
public methods and attributes are:

.. autoclass:: pygaarst.raster.GeoTIFF
    :members:
    :undoc-members:
    
HDF4 and HDF-EOS
================
[TBC]

HDF5
====
Pygaarst :mod:`raster` module provides a custom :py:class:`HDF5` class
with methods and properties that aim at making it easy to open and process
files in 

.. autoclass:: pygaarst.raster.HDF5
    :members:
    :undoc-members:
