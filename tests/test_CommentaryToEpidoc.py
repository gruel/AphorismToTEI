import os
import sys
from collections import OrderedDict
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

    # ################# open_document ###################

    # ################# divide_document ###################

    def test_divide_document(self):

        # Read test introduction
        with open(path_testdata + 'introduction.txt', 'r',
                  encoding="utf-8") as f:
            introduction = f.read().strip()

        # Read test title
        with open(path_testdata + 'title.txt', 'r',
                  encoding="utf-8") as f:
            title = f.read().strip()

        # Read test text
        with open(path_testdata + 'text.txt', 'r',
                  encoding="utf-8") as f:
            text = f.read().strip()

        # Read test footnotes
        with open(path_testdata + 'footnotes.txt', 'r',
                  encoding="utf-8") as f:
            footnotes = f.read().strip()

        # Read full text file
        with open(path_testdata +
                  'aphorysm_with_intro_title_text_footnotes.txt', 'r',
                  encoding="utf-8") as f:
            self.comtoepi.text = f.read().strip()

        self.comtoepi.divide_document()
        self.assertEqual(self.comtoepi.introduction, introduction)
        self.assertEqual(self.comtoepi.title, title)
        self.assertEqual(self.comtoepi.text, text)
        self.assertEqual(self.comtoepi.footnotes, footnotes)

    def test_divide_document_no_intro(self):

        # Read test title
        with open(path_testdata + 'title.txt', 'r',
                  encoding="utf-8") as f:
            title = f.read().strip()

        # Read test text
        with open(path_testdata + 'text.txt', 'r',
                  encoding="utf-8") as f:
            text = f.read().strip()

        # Read test footnotes
        with open(path_testdata + 'footnotes.txt', 'r',
                  encoding="utf-8") as f:
            footnotes = f.read().strip()

        # Read full text file
        with open(path_testdata +
                  'aphorysm_no_intro_title_text_footnotes.txt', 'r',
                  encoding="utf-8") as f:
            self.comtoepi.text = f.read().strip()

        self.comtoepi.divide_document()
        self.assertEqual(self.comtoepi.title, title)
        self.assertEqual(self.comtoepi.text, text)
        self.assertEqual(self.comtoepi.footnotes, footnotes)


    def test_divide_document_no_footnotes(self):

        # Read test title
        with open(path_testdata + 'title.txt', 'r',
                  encoding="utf-8") as f:
            title = f.read().strip()

        # Read test text
        with open(path_testdata + 'text.txt', 'r',
                  encoding="utf-8") as f:
            text = f.read().strip()

        # Read full text file
        with open(path_testdata +
                  'aphorysm_no_intro_title_text_no_footnotes.txt', 'r',
                  encoding="utf-8") as f:
            self.comtoepi.text = f.read().strip()

        self.assertRaises(CommentaryToEpidocException,
                          self.comtoepi.divide_document)

    # ################# read_template ###################

    def test_read_template_missing_template(self):
        self.comtoepi.template_folder = 'ttttt'

        with self.assertRaises(SystemExit) as cm:
            self.comtoepi.read_template()
        self.assertEqual(cm.exception.code, 1)

    def test_read_template(self):
        # Read the template comparison manually
        with open(path_testdata + 'xml_template.txt', 'r') as f:
            template = f.read()
        # split it as in the method
        part1, sep, part2 = template.partition(self.comtoepi.template_marker)

        self.comtoepi.template_folder = path_testdata
        self.comtoepi.read_template()
        self.assertEqual(part1, self.comtoepi.template_part1)
        self.assertEqual(part2, self.comtoepi.template_part2)

    # ################# _references ###################

    def test__references(self):
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

    # ################# _omission ###################

    def test__omission(self):
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

    # ################# _addition ###################

    def test__addition(self):
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

    # ################# _correxi ###################

    def test__correxi(self):
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

    # ################# _conieci ###################

    def test__conieci(self):
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

    # ################# _standard_variant ###################

    def test__standard_variant(self):
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

    # ################# _footnotes ###################

    def test__footnotes(self):
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

        # convert the footnotes in OrderDict
        # key is equale to the numeration of the footnote
        self.comtoepi.footnotes = OrderedDict([(i+1, _tmp)
                                               for i, _tmp
                                               in enumerate(footnotes_in)])
        # Run the function with the input
        main_out, app_out = self.comtoepi._footnotes(text_in)

        # Convert the output lists to strings with each element on a new line
        main_out = '\n'.join(main_out)
        app_out = '\n'.join(app_out)

        # Test the return value matches the expected output
        self.assertEqual(main_out, main_ref)
        self.assertEqual(app_out, app_ref)

    # ################# process_file ###################

    def test_process_file_bad_format(self):
        self.comtoepi.folder = path_testdata
        self.comtoepi.fname = 'bug_break_file_name_test.txt'
        self.assertRaises(CommentaryToEpidocException,
                          self.comtoepi.process_file)

    # ################# process_folder ###################

    def test_process_folder(self):
        self.assertTrue(self.comtoepi.process_folder(path_testdata))

    def test_process_folder_raise_error_folder_not_present(self):
        folder = os.path.join('path_failed')
        self.assertRaises(CommentaryToEpidocException,
                          self.comtoepi.process_folder,
                          folder)

if __name__ == '__main__':
    pytest.main()
