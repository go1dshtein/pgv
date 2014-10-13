#!/usr/bin/env python
from setuptools import setup


setup(name='pgv',
      version='0.0.2',
      description="PostgreSQL schema versioning tool",
      long_description=open("README.rst").read(),
      author='Kirill Goldshtein',
      author_email='goldshtein.kirill@gmail.com',
      packages=['pgv', 'pgv.utils', 'pgv.vcs_provider'],
      package_dir={'pgv': 'pgv'},
      package_data={'pgv': ['data/init.sql']},
      install_requires=['GitPython >= 0.3.1', 'psycopg2', "PyYAML"],
      test_suite='tests',
      scripts=['bin/pgv'],
      license='GPLv2',
      url='https://github.com/go1dshtein/pgv',
      classifiers=['Intended Audience :: Developers',
                   'Environment :: Console',
                   'Programming Language :: Python :: 2.7',
                   'Natural Language :: English',
                   'Development Status :: 1 - Planning',
                   'Operating System :: Unix',
                   'Topic :: Utilities'])
