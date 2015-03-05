try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
 
setup(  
    name='pygaarst',
    version='0.0.1',
    description='Tools for geospatial analysis and remote sensing',
    author='Chris Waigl',
    author_email='chris.waigl@gmail.com',
    url='https://github.com/chryss/pygaarst',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        # Uses dictionary comprehensions ==> 2.7 only
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: GIS',
    ],
    packages=['pygaarst'],
    package_data={
        'pygaarst': ['Hyperion_Spectral_Coverage.tab'],
    },
    #tests_require=['pytest'],
    extras_requires = {
        'all_raster': ['numpy', 'GDAL', 'pyproj'],
        'hdf4': ['numpy', 'GDAL', 'pyproj', 'python-hdf4'],
        'hdf5': ['numpy', 'GDAL', 'pyproj', 'h5py'],
        'vectoroverlay': ['numpy', 'GDAL', 'shapely', 'fiona'],
        'plot': ['matplotlib', 'mpl_toolkits.basemap'],
    },
    )