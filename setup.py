#!/usr/bin/env python

# -----------------------------------------------------------------------------
# Copyright (c) 2016, Wetlab Assistant Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from setuptools import find_packages, setup


classes = """
    Development Status :: 1 - Pre-Alpha
    License :: OSI Approved :: BSD License
    Topic :: Software Development :: Libraries
    Topic :: Scientific/Engineering
    Topic :: Scientific/Engineering :: Bio-Informatics
    Programming Language :: Python :: 3
    Programming Language :: Python :: 3 :: Only
    Programming Language :: Python :: 3.4
    Programming Language :: Python :: 3.5
    Operating System :: Unix
    Operating System :: POSIX
    Operating System :: MacOS :: MacOS X
"""
classifiers = [s.strip() for s in classes.split('\n') if s]

setup(name='bloom_analyses',
      version='1.0',
      license='BSD-3-Clause',
      description='Wetlab Assistant',
      long_description='Weblab Assistant',
      author="wetlab assistant development team",
      author_email="qiyunzhu@@gmail.com",
      maintainer="wetlab assistant development team",
      maintainer_email="qiyunzhu@@gmail.com",
      packages=find_packages(),
      include_dirs=[np.get_include()],
      install_requires=[],
      classifiers=classifiers,
      package_data={
          }
      )-
