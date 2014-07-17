#!/usr/bin/env python
import os
from setuptools import setup

try:
    import pypandoc
    description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    description = open('README.md').read()

setup(name='pgv',
      version='0.0.1',
      description=description,
      author='Kirill Goldshtein',
      author_email='goldshtein.kirill@gmail.com',
      packages=['pgv'],
      package_dir={'pgv': 'pgv'},
      package_data={'pgv': ['init/init.sql']},
      install_requires=['GitPython >= 0.3.1', 'psycopg2', "PyYAML"],
      test_suite='tests',
      scripts=['bin/pgv'],
      license='GPL',
      classifiers=['Intended Audience :: Developers',
                   'Environment :: Console',
                   'Programming Language :: Python :: 2.7',
                   'Natural Language :: English',
                   'Development Status :: 1 - Planning',
                   'Operating System :: Unix',
                   'Topic :: Utilities'])
