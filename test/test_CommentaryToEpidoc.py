import os
import unittest

# TODO: Move to proper Data set directory. UGLY HACK but it worked :)
# TODO: modify the default path of the unittest so it is working with
# pycharm
path = os.path.realpath(__file__)
directory = os.path.dirname(path)

path_testdata = directory + os.sep + 'Data'
os.chdir(path_testdata)

from hyppocratic import CommentaryToEpidoc


class TestCommentaryToepidoc(unittest.TestCase):

    def test_process_references(self):
        pass

    def test_process_omission(self):
        pass

    def test_process_addition(self):
        pass

    def test_process_correxi(self):
        pass

    def test_process_conieci(self):
        pass

    def test_process_standard_variant(self):
        pass

    def test_process_footnotes(self):
        pass