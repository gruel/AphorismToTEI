import os
import unittest

from hyppocratic import CommentaryToEpidoc

# TODO: Move to proper Data set directory. UGLY HACK but it worked :)
# TODO: modify the default path of the unittest so it is working with pycharm
path = os.path.realpath(__file__)
directory = os.path.dirname(path)
path_testdata = directory + os.sep + 'test_files' + os.sep
os.chdir(path_testdata)


class TestCommentaryToEpidoc(unittest.TestCase):

    def test_process_references(self):
        """
        Runs the function process_references(...) on the text in
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
        text_out = CommentaryToEpidoc.process_references(text_in)

        self.assertEqual(text_out, text_ref)

    def test_process_omission(self):
        """
        Runs the function process_omission(...) on the text in
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
        CommentaryToEpidoc.process_omission(text_in, list_out)

        # Convert the output list to a string with each element on a new line
        # This is not good in a test you should not modify the results
        # before the test.
        text_out = '\n'.join(list_out)

        self.assertEqual(text_out, text_ref)

    def test_process_addition(self):
        """
        Runs the function process_addition(...) on the text in
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
            CommentaryToEpidoc.process_addition(text_in, list_out)

            # Convert the output list to a string with each element
            # on a new line
            text_out = '\n'.join(list_out)

            self.assertEqual(text_out, text_ref)

    def test_process_correxi(self):
        """
        Runs the function process_correxi(...) on the text in
        test_process_correxi1.in and test_process_correxi2.in, and compares the output
        against the text in test_process_correxi1.ref and test_process_correxi2.ref
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
            CommentaryToEpidoc.process_correxi(text_in, list_out)

            # Convert the output list to a string with each element on a new line
            text_out = '\n'.join(list_out)

            self.assertEqual(text_out, text_ref)

    def test_process_conieci(self):
        """
        Runs the function process_conieci(...) on the text in
        test_process_conieci1.in and test_process_conieci2.in, and compares the output
        against the text in test_process_conieci1.ref and test_process_conieci2.ref
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
            CommentaryToEpidoc.process_conieci(text_in, list_out)

            # Convert the output list to a string with each element on a new line
            text_out = '\n'.join(list_out)

            self.assertEqual(text_out, text_ref)

    def test_process_standard_variant(self):
        """
        Runs the function process_standard_variant(...) on the text in
        test_process_standard_variant.in, and compare the output against the text in
        test_process_standard_variant.ref
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
        CommentaryToEpidoc.process_standard_variant(text_in, list_out)

        # Convert the output list to a string with each element on a new line
        text_out = '\n'.join(list_out)

        # Test the return value matches the expected output
        self.assertEqual(text_out, text_ref)

    def test_process_footnotes(self):
        """
        Runs the function process_footnotes(...) on the text in
        test_process_footnotes_string.in (which contains a fabricated text string) and
        test_process_footnotes_fn.in (which contains fabricated footnotes), and
        compares the output against the text in test_process_footnotes.ref
        """

        # Load text string from input file
        with open(path_testdata + 'test_process_footnotes_str.in', 'r',
                  encoding="utf-8") as f:
            text_in = f.read()

        # Load footnotes string from input file and convert to list
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

        # Run the function with the input
        main_out, app_out, junk = \
            CommentaryToEpidoc.process_footnotes(text_in, 1, footnotes_in)

        # Convert the output lists to strings with each element on a new line
        main_out = '\n'.join(main_out)
        app_out = '\n'.join(app_out)

        # Test the return value matches the expected output
        self.assertEqual(main_out, main_ref)
        self.assertEqual(app_out, app_ref)