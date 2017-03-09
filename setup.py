#!/usr/bin/env python

#TODO: add data in the installation for the default xml_template.txt

from setuptools import setup

import os

setup(name='hyppocratic',
      version='0.1',
      description='Software to convert text files to EpiDoc compatible XML.',
      author='Johathan Boyle, Nicolas Gruel',
      packages=['hyppocratic'],
      install_requires=['docopt', 'nose', 'pytest'],
      entry_points={
          'console_scripts': [
              'AphorismsToTEI = hyppocratic.main:main']
                    }
      )

# TODO: python setup.py does not use setup.cfg. Need to investigate

# Run the test should be put before if failed abort installation?
#os.system('py.test')
# TODO: add pytest here see documentation.