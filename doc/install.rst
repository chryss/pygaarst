***************
Getting started
***************

Prerequisites
=============

As of now, Pygaarst requires Python 2.7. Python 3 (probably >= 3.3) 
is on the roadmap.

In case you only need the Landsat/Hyperion/ALI metadata parsing features or
the client for the NASA MODAPS API there are no dependencies on external
libraries.

The following Python packages are required for using any raster manipulation
functionality. This includes having the corresponding binary libraries
installed:

- numpy
- pyproj
- GDAL 

The following Python packages are prerequisites for optional functionality:

- h5py (for reading and processing HDF5 files such as VIIRS scenes)
- python-hdf4 (for reading and processing HDF4 files such as MODIS scenes
  -- but in its absence, GDAL will be tried)
- matplotlib (for plotting)
- mpl_toolkits.basemap (for plotting on a map)
- pytest (for unit tests)
- fiona (for reading and processing GIS vector files)
- shapely (for operations on vector data)

Future functionality is expected to require the following packages:

- netCDF4 (for reading and processing NetCDF files)

**Please note** that installing the prerequisites may, depending on your
configuration, require some planning:

- Installing **Numpy** via ``pip`` will require a C and a Fortran 77 compiler to build the extension modules. A good alternative is to use `a binary distribution`_. The same is true for `Matplotlib`_.
- **GDAL**, **pyproj**, **h5py**, **python-hdf4**, **netCDF4** and **GEOS** (which is a prerequisite for shapely and the Basemap toolkit) require libraries to be installed before the Python bindings can be installed. The easiest way to do this in a consistent manner is often to use a package manager on GNU/Linux or OS X. For Windows, binary packages are available.
- The **Basemap** toolkit for Matplotlib is a very large install. For Windows, a binary package is available. For GNU/Linux and OS X, it needs to be built from source. If you don't need to plot on maps, you don't need it!
- In many cases, it may be easiest to install a complete scientific Python
software package such as the Enthought Python Distribution or Anaconda, 
or to use a package manager (on GNU/Linux or OS X) There is one exception to
this: Pygaarst can use GDAL to access HDF-EOS (HDF4) files such as MODIS and
ASTER L1B data and georeference files. GDAL is, however, not by default 
compiled with HDF4 support. On OS X, it is rather difficult to install a GDAL 
with HDF4 support via either Homebrew or the Anaconda Python distribution. The 
`frameworks provided by kyngchaos`_, while otherwise a sub-optimal way to 
provide the necessary environment, however, have the required support.

To account for individual user preferences, dependencies are listed in
``setup.py`` as optional (using the ``extras_required`` key) for automatic
install. The ``requirements.txt`` file lists them, however, and can be used 
to install them via ``pip``. You may edit ``requirements.txt`` to comment out 
the optional dependencies you **know** you won't need.

My personal installation flow, which works well on OS X is to:

- first install all the system libraries with the correct support options 
- then install the Python packages via ``pip`` 

Pygaarst is distributed under the terms of the `MIT License`_.

.. _frameworks provided by kyngchaos: http://www.kyngchaos.com/software/frameworks
.. _MIT License: http://opensource.org/licenses/MIT
.. _a binary distribution : http://docs.scipy.org/doc/numpy/user/install.html
.. _Matplotlib: http://matplotlib.org/1.3.1/users/installing.html

Installation
============

The use of a virtualenv_ is recommended.

At the current stage, there is no stable release for Pygaarst yet. The latest code from the master branch can be installed via::

    $ pip install git+https://github.com/chryss/pygaarst.git

.. _virtualenv: http://www.virtualenv.org/en/latest/

Usage example
=============

A step-by-step example of using :mod:`pygaarst.raster` to access and plot
VIIRS and Landsat data is worked through in `this IPython Notebook`_.

.. _this IPython Notebook: http://nbviewer.ipython.org/gist/anonymous/7593127