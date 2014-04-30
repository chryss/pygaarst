*****************************************
Working with specific remote sensing data
*****************************************

Landsat
=======

Usage
-----
Pygaarst offers an intuitive and friendly way to access Landsat scene data 
and metadata as distributed as at-sensor scaled radiance data files ("Level1")
in GeoTIFF format, one file per imaging band, as zipped tar archives.

The work is done by two classes: :class:`Landsatscene`, which takes the name 
of the unzipped data directory, and :class:`Landsatband`, which can be
instantiated from a :class:`Landsatscene` object::

    >>> from pygaarst import raster
    >>> basedir = "path/to/data"
    >>> landsatscene = "LE70690142004201EDC01"
    >>> sc = raster.Landsatscene(os.path.join(basedir, landsatscene))
    >>> type(sc)
    <class 'pygaarst.raster.Landsatscene'>
    >>> b2 = sc.band2
    >>> type(b2.data)
    <type 'numpy.ndarray'>
    >>> b2.data.shape
    (8021, 8501)

The :class:`Landsatscene` knows how to calculate often used radiometric 
quantities such as vegetation indices, or access the Landsat metadata. Both `old and new metadata format`_ is supported::

    >>> ndvi = sc.NDVI
    >>> type(ndvi)
    <type 'numpy.ndarray'>
    >>> sc.meta['IMAGE_ATTRIBUTES']['SUN_ELEVATION']
    44.26873508
    >>> sc.meta['PRODUCT_METADATA']['DATE_ACQUIRED']
    datetime.date(2004, 7, 19)

:class:`Landsatscene` also supports a filename infix in case all scene
files have been pre-processed. A typical example would be if the GeoTIFF band
files have been sub-setted and saved under a new file name that adds 
a label at the end of the filename, before the extension. For example:

    >>> b2.data.shape
    (8021, 8501)
    >>> sc.infix = '_CLIP'
    >>> b3 = sc.band3
    >>> b3.data.shape
    (347, 373)
    >>> b2.filepath
    'path/to/data/LE70690142004201EDC01_B2.TIF'
    >>> b3.filepath
    'path/to/data/LE70690142004201EDC01_B3_CLIP.TIF'

The :class:`Landsatband` object knows its own geographic attributes and can 
translate the raw data into radiance and reflectance. For thermal IR bands,
calculation of radiant (brightness) temperatures is supported::

    >>> b3.radiance
    array([[ 23.59606299,  24.83937008,  23.59606299, ...,  29.81259843,
             29.81259843,  29.81259843],
           [ 25.46102362,  24.21771654,  23.59606299, ...,  30.43425197,
             30.43425197,  29.19094488],
           ..., 
           [ 41.0023622 ,  39.75905512,  40.38070866, ...,  90.11299213,
             91.35629921,  92.5996063 ],
           [ 40.38070866,  38.51574803,  41.0023622 , ...,  90.11299213,
             90.73464567,  90.73464567]])
    >>> b3.Lat
    array([[ 65.23978665,  65.23979005,  65.23979346, ...,  65.24086228,
             65.24086467,  65.24086706],
           [ 65.2400558 ,  65.2400592 ,  65.24006261, ...,  65.24113144,
             65.24113383,  65.24113622],
           ..., 
           [ 65.33291157,  65.332915  ,  65.33291841, ...,  65.3339918 ,
             65.3339942 ,  65.3339966 ],
           [ 65.33318072,  65.33318414,  65.33318756, ...,  65.33426096,
             65.33426336,  65.33426576]])
    >>> b6 = sc.band6L
    >>> b6.tKelvin
    array([[ 298.51857637,  298.51857637,  299.01776653, ...,  301.97175896,
             301.48420756,  301.48420756],
           [ 297.51409689,  298.01736166,  298.51857637, ...,  302.45745107,
             301.97175896,  301.48420756],
           ..., 
           [ 294.96609241,  294.96609241,  294.96609241, ...,  290.23752626,
             290.77248753,  290.23752626],
           [ 294.96609241,  294.96609241,  294.96609241, ...,  290.77248753,
             290.77248753,  290.77248753]])

All parameters
are, where provided, taken from the scene-specific metadata. Where not, 
they are taken from the published literature.

.. _old and new metadata format: http://landsat.usgs.gov/Landsat_Metadata_Changes.php


The Landsatscene class
----------------------
.. autoclass:: pygaarst.raster.Landsatscene
    :members:
    :undoc-members:
    
The Landsatband class
---------------------

.. autoclass:: pygaarst.raster.Landsatband
    :members:
    :undoc-members:

EO-1 Hyperion, ALI and general USGS Level 1 data
================================================

Hyperion and ALI
----------------

Hyperion imaging spectroscopy data and ALI multi-spectral imagery, processed
to a Level 1 product, are distributed by the USGS in a format very similar to
Landsat data. Pygaarst provides classes similar to the Landsat-specific 
classes for these sensors. 

.. autoclass:: pygaarst.raster.Hyperionscene
    :members:
    :undoc-members:
    
.. autoclass:: pygaarst.raster.Hyperionband
    :members:
    :undoc-members:

.. autoclass:: pygaarst.raster.ALIscene
    :members:
    :undoc-members:
    
.. autoclass:: pygaarst.raster.ALIband
    :members:
    :undoc-members:


The USGSL1 parent classes
-------------------------
All of them inherit from parent classes called 
:class:`USGSL1scene` and :class:`USGSL1band` respectively.

.. autoclass:: pygaarst.raster.USGSL1scene
    :members:
    :undoc-members:
    
.. autoclass:: pygaarst.raster.USGSL1band
    :members:
    :undoc-members:

The metatadata parser
---------------------
All these USGS-provided satellite remote sensing data use essentially the same
metadata format. It is provided in a text file that can be recognized by the 
letters *MTL* in the filename. The data structure is nested naturally maps 
onto a dictionary of dictionaries, with unlimited nesting depth. Unfortunately
it appears to be quite badly documented, or in any event I have been unable
to locate a data description or specification.

For objects of type :class:`pygaarst.raster.USGSL1scene` or its children 
(:class:`pygaarst.raster.Landsatscene`, :class:`pygaarst.raster.ALIscene` 
or :class:`pygaarst.raster.Hyperionscene`), the parsed metadata dictionary is
provided in the `meta` attribute::

    >>> print sc.meta
    {'IMAGE_ATTRIBUTES': {'GEOMETRIC_RMSE_MODEL': 2.868, 'CLOUD_COVER': 31.0, 'GEOMETRIC_RMSE_MODEL_X': 1.73, 'SUN_AZIMUTH': 162.9104406, 'SUN_ELEVATION': 44.26873508, 'GROUND_CONTROL_POINTS_MODEL': 210, 'IMAGE_QUALITY': 9, 'GEOMETRIC_RMSE_MODEL_Y': 2.287}, 'RADIOMETRIC_RESCALING': {'RADIANCE_MULT_BAND_7': 0.044, 'RADIANCE_MULT_BAND_5': 0.126, 'RADIANCE_MULT_BAND_4': 0.969, ...
    
The parser is implemented via the module :mod:`pygaarst.mtlutils`. An 
arbitrary MTL file can be parsed by calling
:func:`pygaarst.mtlutils.parsemeta()`:

.. automodule:: pygaarst.mtlutils
    :members:

MODIS swath data
================
*[This is a little harder...]*

Suomi/NPP VIIRS 
===============
.. autoclass:: pygaarst.raster.VIIRSHDF5
    :members:
    :undoc-members:

MODAPS data download API client
===============================
This is a REST-full web service client that implements the NASA LAADSWEB data API (http://ladsweb.nascom.nasa.gov/data/api.html). Usage::

    >>> from pygaarst import modapsclient as m
    >>> a = m.ModapsClient()
    >>> retvar = a.[methodname](args)

.. automodule:: pygaarst.modapsclient
    :members:
    :undoc-members:

