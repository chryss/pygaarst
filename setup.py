try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
 
setup(name='pygaarst',
      version='0.0.1',
      description='Tools for geospatial analysis and remote sensing',
      author='Chris Waigl',
      author_email='chris.waigl@gmail.com',
      url='https://github.com/chryss/pygaarst',
      packages=['pygaarst'],
     )