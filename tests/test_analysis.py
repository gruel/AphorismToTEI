import os
import sys
import unittest
import pytest

from context import analysis

file_path = os.path.realpath(__file__)
path = os.path.dirname(file_path)
sys.path.append(path)

path_testdata = os.path.join(path, 'test_files') + os.sep
# examples = os.path.join(path, '..', 'Examples', 'TextFiles') + os.sep
template_file = os.path.join(path, '..', 'hyppocratic', 'xml_template.txt')


class TestProcess(unittest.TestCase):

    def test_references(self):
        """
        Runs the function _references(...) on the text in
        test_process_references.in, and compares the output against the text in
        test_process_references.ref
        """
        # Load text from input file
        with open(path_testdata + 'test_process_references.in', 'r',
                  encoding="utf-8") as f:
            text_in = f.read()

        # Load text from reference file
        with open(path_testdata + 'test_process_references.ref', 'r',
                  encoding="utf-8") as f:
            text_ref = f.read()

        # Run the function with the input
        text_out = analysis.references(text_in)

        self.assertEqual(text_out, text_ref)

