"""
Module to
"""


import os
import sys
# sys.path.insert(0, os.path.abspath('..'))
file_path = os.path.realpath(__file__)
path = os.path.dirname(file_path) + os.sep + '..'
sys.path.append(path)

import hyppocratic
from hyppocratic.aphorisms_to_xml import Process, \
    AphorismsToXMLException

# Module
from hyppocratic.footnotes import Footnote, Footnotes, FootnotesException
import hyppocratic.analysis as analysis
import hyppocratic.title as title