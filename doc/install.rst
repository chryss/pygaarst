***************
Getting started
***************

Prerequisites
=============

As of now, Pygaarst has only been run under Python 2.7. Making it work for 
2.6 doesn't appear to be a high priority. Python 3 (probably >= 3.3 or 3.4) 
is on the roadmap.

The following Python packages are required, including their dependencies and 
any binary libraries:

- numpy
- pyproj
- GDAL 

The following Python packages are prerequisites for optional functionality:

- h5py (for reading and processing HDF5 files)
- matplotlib (for plotting)
- mpl_toolkits.basemap (for plotting on a map)
- pytest (for unit tests)

Future functionality is expected to require the following packages:

- netCDF4 (for reading and processing NetCDF files)
- fiona (for reading and processing GIS vector files)
- shapely (for operations on vector data)

**Please note** that several of the required packages rely on libraries that 
need to be installed either manually or through a suitable package manager 
beforehand (GDAL, PROJ4, NetCDF, HDF5), require quite a bit of compilation 
(Numpy, Matplotlib) or are very large (mpl_toolkits.basemap). 
Depending on your environment, the effort to install them may vary -- 
they usually come with the large pre-packaged scientific Python distributions. 
Therefore, these dependencies are not listed in ``setup.py``. 
For OS X users, the `frameworks provided by kyngchaos`_ may be helpful. 
For GDAL, in particular, the default options provided by package managers 
such as Homebrew may not install the more obscure scientific data formats
that you may be needing (in particular, HDF-EOS for NASA satellite data).

Pygaarst is distributed under the terms of the `MIT License`_.

.. _frameworks provided by kyngchaos: http://www.kyngchaos.com/software/frameworks
.. _MIT License: http://opensource.org/licenses/MIT

Installation
============

The use of a virtualenv_ is recommended.

At the current stage, there is no stable release for Pygaarst yet. The latest code from the master branch can be installed via::

    $ pip install git+https://github.com/chryss/pygaarst.git

.. _virtualenv: http://www.virtualenv.org/en/latest/

Usage example
=============

