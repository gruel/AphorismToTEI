import os
import sys
import unittest
import pytest

from context import title

file_path = os.path.realpath(__file__)
path = os.path.dirname(file_path)
sys.path.append(path)

path_testdata = os.path.join(path, 'test_files') + os.sep
# examples = os.path.join(path, '..', 'Examples', 'TextFiles') + os.sep
template_file = os.path.join(path, '..', 'hyppocratic', 'xml_template.txt')

with open(path_testdata + 'title.txt', 'r', encoding='utf-8') as f:
    mock_title = f.read()


class TestTitle(unittest.TestCase):

    def setUp(self):
        self.title = title.Title(mock_title)

    def test_xml_main_failed_witness(self):
        self.title.title = 'WWWW]' + mock_title
        print(self.title.title)
        self.title.xml_main()
        raise