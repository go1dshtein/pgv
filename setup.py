#!/usr/bin/env python
from setuptools import setup


setup(name='pgv',
      version='0.0.1',
      description="PostgreSQL schema versioning tool",
      author='Kirill Goldshtein',
      author_email='goldshtein.kirill@gmail.com',
      packages=['pgv'],
      package_dir={'pgv': 'pgv'},
      package_data={'pgv': ['data/init.sql']},
      install_requires=['GitPython >= 0.3.1', 'psycopg2', "PyYAML"],
      test_suite='tests',
      scripts=['bin/pgv'],
      license='GPLv2',
      classifiers=['Intended Audience :: Developers',
                   'Environment :: Console',
                   'Programming Language :: Python :: 2.7',
                   'Natural Language :: English',
                   'Development Status :: 1 - Planning',
                   'Operating System :: Unix',
                   'Topic :: Utilities'])
