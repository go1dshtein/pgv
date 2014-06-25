#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(name='pgv',
      version='0.1',
      description='This package provides utility for '
                  'PostgreSQL schema versioning',
      author='Kirill Goldshtein',
      author_email='goldshtein.kirill@gmail.com',
      packages=['pgv'],
      package_dir={'pgv': 'pgv'},
      # package_data={'patch_db.database': ['sql/*.sql', 'sql/*.psql']},
      requires=['GitPython >= 0.3.1', 'psycopg2'],
      test_suite='tests',
      scripts=['bin/pgv'],
      license='GPL',
      classifiers=['Intended Audience :: System Administrators',
                   'Environment :: Console',
                   'Programming Language :: Python :: 2.7',
                   'Natural Language :: English',
                   'Development Status :: 1 - Planning',
                   'Operating System :: Unix',
                   'Topic :: System :: Networking',
                   'Topic :: Utilities'])
