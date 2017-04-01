#!/usr/bin/env python

import re
import sys

from setuptools import setup, find_packages


def version():
    with open('roboticia_quattro/_version.py') as f:
        return re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read()).group(1)

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

setup(

      name='roboticia-quattro',
      version=version(),
      packages=find_packages(),
      install_requires=['pypot >= 3.0', 'hampy'],
      setup_requires=['setuptools_git >= 0.3', ],
      include_package_data=True,
      exclude_package_data={'': ['.gitignore']},
      zip_safe=False,
      author='Julien JEHL',
      author_email='contact@roboticia.com',
      description='Roboticia horse Software Library',
      url='https://github.com/roboticia/horse',
      license='GNU GENERAL PUBLIC LICENSE Version 3',

      **extra
      )
