pygaarst
========================================================

**Python geospatial analysis and remote sensing toolkit**

The pygaarst package is a Python library that aims at simplifying the manipulation of 
remote sensing and other geospatial data. Features include data and metadata access; 
georeferencing; combining raster and vector datasets; re-projecting with Proj4; 
mapping and plotting with Matplotlib. pygaarst relies heavily on numpy for data 
structures and GDAL for data access and geospatial handling. Its major goal is to 
provide a set of friendly APIs that make common tasks on widely used data formats 
easy to accomplish in few lines of code.

The project was initiated on 2013-09-18 and in an early stage of development.

Dependencies
------------

* GDAL for gdal, ogr and osr
* pyproj
* numpy,
* matplotlib and mpl_toolkits.basemap for `pygaarst.basemaputils`
* netCDF4, pyhdf and h5py -- for netCDF, HDF4, HDF5 and HDF-EOS
* [future] shapely, fiona, descartes 
* [future] most likely an XML parser of some sort 

Documentation is also still in the very early stages of development.

The following modules are available and fulfil useful functions at the current time:

pygaarst.modapsclient
---------------------

This is a REST-full web service client that implements the NASA LAADSWEB data API (http://ladsweb.nascom.nasa.gov/data/api.html)

`class ModapsClient(object)`

Usage:

```python
from pygaarst import modapsclient as m
a = m.ModapsClient()
retvar = a.[methodname](args)
```

Implements the methods from http://ladsweb.nascom.nasa.gov/data/api.html , except for (currently) those related to OpenSearch (which don't appear to be working reliably server-side) and ordering (TBD). Implemented methods are marked with an x. 

* x `getAllOrders`  
* x `getBands`  
* x `getBrowse`  
* x `getCollections`  
* x `getDataLayers`  
* x `getDateCoverage`  
* x `getFileOnlineStatuses`  
* x `getFileProperties`  
* x `getFileUrls`  
* x `getMaxSearchResults`  
* `getOpenSearch`  
* `getOrderStatus`  
* `getOrderUrl`  
* `getOSDD`  
* x `getPostProcessingTypes`  
* x `listCollections` (deprecated)  
* x `listMapProjections`  
* x `listProductGroups`  
* x `listProducts`  
* x `listProductsByInstrument`  
* x `listReprojectionParameters`  
* x `listSatelliteInstruments`  
* `orderFiles`  
* `orderFilesProcessed` (deprecated)  
* `releaseOrder`  
* `searchDatasets`  
* x `searchForFiles`  
* `searchForFilesByName`  

TODO: ordering

pygaarst.raster
---------------

This module provides several classes to represent common raster dataset formats. Implemented currently:

**`class GeoTiff(object)`**

A generic representation of a GeoTIFF file. 

Args: 
  filepath - path to GeoTiff file
  
**`class HDF5(object)`**

A representation of a HDF5 data file. This is currently tailored to NPP/VIIRS SDR 
or EDR files. 

Args:
  filepath - path to HDF5 file

**`class Landsatscene(object)`**

A representation of a Landsat 4, 5, 7 or 8 scene for TM, ETM+ or OLI/TIRS sensor data. 
Will parse the metadata file in both pre and post August 2012 formats. 

Args:
  dirname - name of the directory to which the scene files are unzipped
  
Individual Landsat bands (for the above sensors and Landsat versions) can be accessed via:

**`class Landsatband(GeoTIFF)`**

A representation of a single-band dataset. Is aware of its metadata. Inherits from `GeoTIFF`.

Further examples are provided in a [tutorial walkthrough] [1] of data access and map plotting for GeoTIFF and HDF5/VIIRS.

TODO:
* move the VIIRS-specific functionality to a separate class
* GeoTIFF improvements: clean handling of multiband datasets
* lat/long and native coordinate arrays for both "middle of pixel" and "corner" specs
* HDF-EOS, HDF4, netCDF 
* MODIS and ASTER swath and gridded data including XML metadata file parsing

  [1]: http://nbviewer.ipython.org/7593127

pygaarst.landsatutils
---------------------

Provides functions used by the `pygaarst.raster.Landsatscene` and `pygaarst.raster.Landsatband` classes, including:

**`pygaarst.landsatutils.get_bands(spacecraftid)`**

Returns permissible band labels (TM, ETM+ or OLI/TIRS) for a given spacecraft (L4, L5, L7 or L8).

**`pygaarst.landsatutils.parsemeta(metadatafilepath)`**

Parses a metadata file and returns a dictionary of metadata values in the same nested
structure as the USGS metadata file decription language.

**`pygaarst.landsatutils.getKconstants(spacecraftid)`**

**`pygaarst.landsatutils.gainbias(lmax, lmin, qcalmax, qcalmin)`**

**`pygaarst.landsatutils.dn2rad(data, gain, bias)`**

**`pygaarst.landsatutils.rad2kelvin(data, k1, k2)`**

**`pygaarst.landsatutils.rad2celsius(data, k1, k2)`**

These utility functions facilitate the conversion of digintal numbers (DN) to radiance
and brighness temperature data. (TODO: reflectance.)

pygaarst.vector
---------------

TODO: 
* `shapefile` class
* `geojson` class

pygaarst.basemaputils
---------------------

`pygaarst.basemaputils.map_interiorAK()` returns a Basmap object for a map of 
the bulk of the Alaska mainland for convenient plotting.

(TODO: Other quick maps, possibility to override more parameters.)
