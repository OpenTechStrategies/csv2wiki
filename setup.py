#!/usr/bin/env python

from distutils.core import setup

setup(name='csv2wiki',
      version='1.0.0',
      description='Open source tool to convert rows in a CSV file to pages in a wiki.',
      author='Open Tech Strategies, LLC',
      author_email='intentionally@left.blank.com',
      url='https://github.com/OpenTechStrategies/csv2wiki-wikis',
      packages=['csv2wiki'],
      install_requires=['mwclient', 'bs4', 'unidecode'])
