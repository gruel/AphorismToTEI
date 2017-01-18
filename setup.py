#!/usr/bin/env python

#TODO: add data in the installation for the default xml_template.txt

from setuptools import setup

setup(name='hyppocratic',
      version='0.1',
      description='Software to convert text files to EpiDoc compatible XML.',
      author='Johathan Boyle, Nicolas Gruel',
      packages=['hyppocratic'],
      install_requires=['docopt'],
      entry_points={
          'console_scripts': [
              'CommentaryToEpidoc = hyppocratic.driver:main']
                    }
      )
