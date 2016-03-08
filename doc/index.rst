.. pygaarst documentation master file, created by
   sphinx-quickstart on Mon Jan 13 12:45:50 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Pygaarst: geospatial analysis and remote sensing tools for Python
=================================================================

Pygaarst is a Python package that is designed to make it easy to access
geospatial raster data such as remote sensing imagery, and perform 
frequently needed processing steps in a human-friendly way. 

Loading data, accessing the intended band or dataset, converting it
to meaningful units and calculating standardised indices should be easy. 
As should be plotting the imagery on a map or combining raster with vector 
datasets, such as ESRI shapefiles.

Some examples:

    >>> from pygaarst import raster
    >>> basedir = "path/to/data"
    >>> landsatscene = "LE70690142004201EDC01"
    >>> sc = raster.Landsatscene(os.path.join(basedir, landsatscene))
    >>> swirband = sc.band7
    >>> type(swirband.data)
    <type 'numpy.ndarray'>
	>>> type(swirband.radiance)
    <type 'numpy.ndarray'>
    >>> swirband.radiance.shape
    (8021, 8501)
	>>> ndvi = sc.ndvi
	
As of the moment this documentation is written, pygaarst is under development 
and not all of the API design should be considered stable. The following 
capabilities are supported:

* Python 2 (2.6+)
* :class:`GeoTiff` base class (in :mod:`pygaarst.raster`), with
  :class:`Landsatband`, :class:`ALIband` and :class:`Hyperionband` 
  inheriting from it
* :class:`Landsatscene`, :class:`Hyperionscene` and :class:`ALIscene` 
  to represent a scene directory as retrieved from the USGS data
  portal
* :class:`VIIRSHDF5` for NPP VIIRS SDS dataset files in HDF5 format,
  as retrieved from NOAA's portalsm inheriting from a generic 
  :class:`HDF5` class
* :class:`MODSWHDF4` for MODIS Swath dataset files in HDF-EOS format,
  inheriting from a generic :class:`HDF4` class 
* Reading georeference files or metadata and calculation of pixel-center
  and, for gridded data, pixel-corner coordinate references 
* A metadata parser for USGS-style MTL files in :mod:`pygaarst.mtlutils`
* Helper methods, functions and properties for frequently
  repeated tasks: transformation to at-sensor radiance and reflectance,
  NDVI and NBR (for Landsat) as well as generic normalized difference
  indices, radiant temperature from thermal infrared bands, calculation 
  and export of radiance spectra for Hyperion, LTK  cloud masking algorithm 
  for Landsat...
* A client for the NASA's modaps data download API in 
  :mod:`pygaarst.modapsclient`

The following capabilities are planned, roughly in order of priority:

* Python 3 support
* Basic geometric and statistical operations involving
  raster and vector structures such as overlays, find-nearest, is-in... 
* MODIS gridded data products and ASTER-specific swath products
* Progressively, other satellite data products

A step-by-step example of using :mod:`pygaarst.raster` to access and plot
VIIRS and Landsat data is worked through in `this IPython Notebook`_.

.. _this IPython Notebook: http://nbviewer.ipython.org/gist/anonymous/7593127
	

:Release: |version|
:Date: |today|

Contents:

.. toctree::
   :maxdepth: 3

   install
   genericraster
   rsraster
   
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

