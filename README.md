pygaarst
========

Tools for geospatial analysis and remote sensing with Python

pygaarst is a library for Python to load and process remote sensing data
in commonly used formats. This includes combining data from different sources,
including GIS vector datasets; re-projecting with Proj4, mapping and plotting 
with Matplotlib. 

It was initiated on 2013-09-18, so it's still in an early stage of development.

There will be multiple dependencies, such as:

* GDAL for gdal, ogr and osr
* pyproj
* numpy, matplotlib and mpl_toolkits.basemap
* shapely, fiona, descartes
* netCDF4, h5py -- for netCDF, HDF5
* etc.

pygaarst.modapsclient
---------------------

Class ModapsClient

Usage:
from pygaarst import modapsclient as m
a = m.ModapsClient()

a.[methodname]

Implements the following methods from http://ladsweb.nascom.nasa.gov/data/api.html (those with x are implemented):


x getAllOrders  
x getBands  
x getBrowse  
x getCollections  
x getDataLayers  
x getDateCoverage  
x getFileOnlineStatuses  
x getFileProperties  
x getFileUrls  
x getMaxSearchResults  
getOpenSearch  
getOrderStatus  
getOrderUrl  
getOSDD  
getPostProcessingTypes  
x listCollections (deprecated)  
x listMapProjections  
x listProductGroups  
x listProducts  
x listProductsByInstrument  
x listReprojectionParameters  
x listSatelliteInstruments  
orderFiles  
orderFilesProcessed (deprecated)  
releaseOrder  
searchDatasets  
x searchForFiles  
searchForFilesByName  