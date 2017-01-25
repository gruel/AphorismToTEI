import os
import sys
import unittest
import pytest

from context import Process, CommentaryToEpidocException

file_path = os.path.realpath(__file__)
path = os.path.dirname(file_path)
sys.path.append(path)

path_testdata = os.path.join(path, 'test_files') + os.sep
# examples = os.path.join(path, '..', 'Examples', 'TextFiles') + os.sep
template_file = os.path.join(path, '..', 'hyppocratic', 'xml_template.txt')


class TestProcess(unittest.TestCase):

    def setUp(self):
        self.comtoepi = Process(n_offset=0, offset_size=4)

    def test_process_references(self):
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
        text_out = self.comtoepi._references(text_in)

        self.assertEqual(text_out, text_ref)

    def test_process_omission(self):
        """
        Runs the function _omission(...) on the text in
        test_process_omission.in, and compare the output against the text in
        test_process_omission.ref
        """

        # Load text from input file
        with open(path_testdata + 'test_process_omission.in', 'r',
                  encoding="utf-8") as f:
            text_in = f.read()

        # Load text from reference file
        with open(path_testdata + 'test_process_omission.ref', 'r',
                  encoding="utf-8") as f:
            text_ref = f.read()

        # Run the function with the input
        list_out = []
        self.comtoepi._omission(text_in, list_out)

        # Convert the output list to a string with each element on a new line
        # This is not good in a test you should not modify the results
        # before the test.
        text_out = '\n'.join(list_out)

        self.assertEqual(text_out, text_ref)

    def test_process_addition(self):
        """
        Runs the function _addition(...) on the text in
        test_process_addition1.in, test_process_addition2.in and
        test_process_addition3.in and compares the output against the text in
        test_process_addition1.ref, test_process_addition2.ref and
        test_process_addition3.ref
        """

        n_test = 3
        basename = path_testdata + 'test_process_addition'

        for test in range(1, n_test + 1):
            # Load text from input file

            with open(basename + str(test) + '.in', 'r', encoding="utf-8") as f:
                text_in = f.read()

            # Load text from reference file
            with open(basename + str(test) + '.ref', 'r', encoding="utf-8") \
                    as f:
                text_ref = f.read()

            # Run the function with the input
            list_out = []
            self.comtoepi._addition(text_in, list_out)

            # Convert the output list to a string with each element
            # on a new line
            text_out = '\n'.join(list_out)

            self.assertEqual(text_out, text_ref)

    def test_process_correxi(self):
        """
        Runs the function _correxi(...) on the text in
        test_process_correxi1.in and test_process_correxi2.in,
        and compares the output against the text in test_process_correxi1.ref
        and test_process_correxi2.ref
        """

        n_test = 2
        basename = path_testdata + 'test_process_correxi'

        for test in range(1, n_test + 1):
            # Load text from input file
            with open(basename + str(test) + '.in', 'r', encoding="utf-8") as f:
                text_in = f.read()

            # Load text from reference file
            with open(basename + str(test) + '.ref', 'r', encoding="utf-8") \
                    as f:
                text_ref = f.read()

            # Run the function with the input
            list_out = []
            self.comtoepi._correxi(text_in, list_out)

            # Convert the output list to a string with each element
            # on a new line
            text_out = '\n'.join(list_out)

            self.assertEqual(text_out, text_ref)

    def test_process_conieci(self):
        """
        Runs the function _conieci(...) on the text in
        test_process_conieci1.in and test_process_conieci2.in, and compares
        the output against the text in test_process_conieci1.ref and
        test_process_conieci2.ref
        """

        n_test = 2
        basename = path_testdata + 'test_process_conieci'
        for test in range(1, n_test + 1):

            # Load text from input file
            with open(basename + str(test) + '.in', 'r', encoding="utf-8") \
                    as f:
                text_in = f.read()

            # Load text from reference file
            with open(basename + str(test) + '.ref', 'r', encoding="utf-8") \
                    as f:
                text_ref = f.read()

            # Run the function with the input
            list_out = []
            self.comtoepi._conieci(text_in, list_out)

            # Convert the output list to a string with each element on a
            # new line
            text_out = '\n'.join(list_out)

            self.assertEqual(text_out, text_ref)

    def test_process_standard_variant(self):
        """
        Runs the function _standard_variant(...) on the text in
        test_process_standard_variant.in, and compare the output against
        the text in test_process_standard_variant.ref
        """

        # Load text from input file
        with open(path_testdata + 'test_process_standard_variant.in', 'r',
                  encoding="utf-8") as f:
            text_in = f.read()

        # Load text from reference file
        with open(path_testdata + 'test_process_standard_variant.ref', 'r',
                  encoding="utf-8") as f:
            text_ref = f.read()

        # Run the function with the input
        list_out = []
        self.comtoepi._standard_variant(text_in, list_out)

        # Convert the output list to a string with each element on a new line
        text_out = '\n'.join(list_out)

        # Test the return value matches the expected output
        self.assertEqual(text_out, text_ref)

    def test_process_footnotes(self):
        """
        Runs the function _footnotes(...) on the text in
        test_process_footnotes_string.in (which contains a fabricated
        text string) and test_process_footnotes_fn.in
        (which contains fabricated _footnotes), and
        compares the output against the text in test_process_footnotes.ref
        """

        # Load text string from input file
        with open(path_testdata + 'test_process_footnotes_str.in', 'r',
                  encoding="utf-8") as f:
            text_in = f.read()

        # Load _footnotes string from input file and convert to list
        with open(path_testdata + 'test_process_footnotes_fn.in', 'r',
                  encoding="utf-8") as f:
            footnotes_in = f.read()
        footnotes_in = footnotes_in.splitlines()

        # Load main XML from reference file
        with open(path_testdata + 'test_process_footnotes_main.ref', 'r',
                  encoding="utf-8") as f:
            main_ref = f.read()

        # Load app XML from reference file
        with open(path_testdata + 'test_process_footnotes_app.ref', 'r',
                  encoding="utf-8") as f:
            app_ref = f.read()

        self.comtoepi.footnotes = footnotes_in
        # Run the function with the input
        main_out, app_out, junk = \
            self.comtoepi._footnotes(text_in, 1)

        # Convert the output lists to strings with each element on a new line
        main_out = '\n'.join(main_out)
        app_out = '\n'.join(app_out)

        # Test the return value matches the expected output
        self.assertEqual(main_out, main_ref)
        self.assertEqual(app_out, app_ref)

    # def test_process_text_files(self):
    #     result = self.comtoepi.process_folder(path_testdata,
    #                                                    template_file,
    #                                                    n_offset=0,
    #                                                    offset_size=4)
    #     self.assertTrue(result)

    def test_process_text_files_no_template(self):
        template_file = 'xml_template.txt'
        self.assertRaises(CommentaryToEpidocException,
                          self.comtoepi.process_folder,
                          path_testdata,
                          template_file)

    def test_process_text_files(self):
        path_testdata = os.path.join('path_failed')
        self.assertRaises(CommentaryToEpidocException,
                          self.comtoepi.process_folder,
                          path_testdata,
                          template_file)

    def test_process_text_file_bad_format(self):
        self.assertRaises(CommentaryToEpidocException,
                          self.comtoepi.process_file,
                          path_testdata,
                          'bug_break_file_name_test.txt',
                          template_file)

if __name__ == '__main__':
    pytest.main()
