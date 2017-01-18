#!/usr/bin/env python

from setuptools import setup

setup(name='hyppocratic',
      version='0.1',
      description='Software to convert text files to EpiDoc compatible XML.',
      author='Johathan Boyle, Nicolas Gruel',
      packages=['CommentaryToEpidoc'],
      install_requires=['docopt'],
      entry_points={
          'console_scripts': [
              'CommentaryToEpidoc = hyppocratic.driver:main']
                    }
      )
