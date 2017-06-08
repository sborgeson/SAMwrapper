# Copyright 2017, Sam Borgeson.
# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
# Direct inquiries to Sam Borgeson (sam@convergenceda.com)

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='SAMwrapper',
      version='0.1',
      description="High level python 2.x and 3.x wrapper around NREL's SAM SDK, a distributed energy simulation engine",
      packages=['SAMwrapper'],
      install_requires=[  'numpy', 'pandas' ],
      author='Sam Borgeson',
      author_email='sam@convergenceda.com',
      license='LICENSE',
      )