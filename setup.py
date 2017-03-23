#!/usr/bin/env python
from setuptools import setup

setup(name='hyppocratic',
      packages=['hyppocratic'],
      version='0.2',
      description=('Software to convert hyppocratic text files '
                   'to in a TEI compatible XML.'),
      long_description='',
      author='Nicolas Gruel, Jonathan Boyle',
      author_email='nicolas.gruel@manchester.ac.uk',
      url='https://github.com/UoMResearchIT/CommentaryToEpidoc',
      classifiers=[
          'Development Status :: 1 - RC',
          'Intended Audience :: Science/Research',
          'Topic :: Text Processing :: Linguistic',
          'Environment :: Console',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Operating System :: Unix',
          'Operating System :: Microsoft',
          'Operating System :: MacOS'
                  ],
      keywords=[],
      install_requires=['docopt'],
      extra_requires={
          'dev': ['pylint', 'pytest', 'pytest-cov', 'testfixtures', 'coverage'],
          'test': ['pytest', 'pytest-cov', 'testfixtures', 'coverage'],
          'doc': ['sphinx', 'numpydoc']},
      entry_points={
          'console_scripts': [
              'AphorismsToTEI = hyppocratic.main:main']
                    },
      package_data={
          'hyppocratic': ['template/xml_template.txt'],
                    },
      license='MIT',
      plateforms='any')
