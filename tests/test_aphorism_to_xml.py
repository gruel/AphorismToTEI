import os
import sys
import unittest
import pytest

from context import Process, AphorismsToXMLException

file_path = os.path.realpath(__file__)
path = os.path.dirname(file_path)
sys.path.append(path)

path_testdata = os.path.join(path, 'test_files') + os.sep
# examples = os.path.join(path, '..', 'Examples', 'TextFiles') + os.sep
template_file = os.path.join(path, '..', 'hyppocratic', 'xml_template.txt')


class TestProcess(unittest.TestCase):

    def setUp(self):
        self.comtoepi = Process()

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
            text = f.readlines()

        # Read test footnotes
        with open(path_testdata + 'footnotes.txt', 'r',
                  encoding="utf-8") as f:
            footnotes = f.readlines()

        # Read full text file
        with open(path_testdata +
                  'aphorism_with_intro_title_text_footnotes.txt', 'r',
                  encoding="utf-8") as f:
            self.comtoepi._text = f.read().strip()

        self.comtoepi.divide_document()

        self.assertEqual(self.comtoepi._introduction, introduction)
        self.assertEqual(self.comtoepi._title, title)
        for i, line in enumerate(self.comtoepi._text.splitlines()):
            self.assertEqual(line.strip(), text[i].strip())
        for i, line in enumerate(self.comtoepi._footnotes.splitlines()):
            self.assertEqual(line.strip(), footnotes[i].strip())

    def test_divide_document_no_intro(self):

        # Read test title
        with open(path_testdata + 'title.txt', 'r',
                  encoding="utf-8") as f:
            title = f.read().strip()

        # Read test text
        with open(path_testdata + 'text.txt', 'r',
                  encoding="utf-8") as f:
            text = f.readlines()

        # Read test footnotes
        with open(path_testdata + 'footnotes.txt', 'r',
                  encoding="utf-8") as f:
            footnotes = f.readlines()

        # Read full text file
        with open(path_testdata +
                  'aphorism_no_intro_title_text_footnotes.txt', 'r',
                  encoding="utf-8") as f:
            self.comtoepi._text = f.read().strip()

        self.comtoepi.divide_document()

        self.assertEqual(self.comtoepi._title, title)
        for i, line in enumerate(self.comtoepi._text.splitlines()):
            self.assertEqual(line.strip(), text[i].strip())
        for i, line in enumerate(self.comtoepi._footnotes.splitlines()):
            self.assertEqual(line.strip(), footnotes[i].strip())

    def test_divide_document_no_footnotes(self):
        # Read full text file
        with open(path_testdata +
                  'aphorism_no_intro_title_text_no_footnotes.txt', 'r',
                  encoding="utf-8") as f:
            self.comtoepi._text = f.read().strip()

        self.assertRaises(AphorismsToXMLException,
                          self.comtoepi.divide_document)

    # ################# read_template ###################

    def test_read_template_missing_template(self):
        self.comtoepi.template_fname = 'ttttt'

        self.assertRaises(AphorismsToXMLException,
                          self.comtoepi.read_template)
        # with self.assertRaises(SystemExit) as cm:
        #     self.comtoepi.read_template()
        # self.assertEqual(cm.exception.code, 1)

    def test_read_template(self):
        # Read the template comparison manually
        with open(path_testdata + 'xml_template.txt', 'r') as f:
            template = f.read()
        # split it as in the method
        part1, sep, part2 = template.partition(self.comtoepi.template_marker)

        self.comtoepi.read_template()
        self.assertEqual(part1, self.comtoepi._template_part1)
        self.assertEqual(part2, self.comtoepi._template_part2)

    def test_read_template_badsep(self):
        self.comtoepi.template_marker = 'xxxx'
        self.assertRaises(AphorismsToXMLException,
                          self.comtoepi.read_template)

    # #################### save_xml #########################

    def test_save_xml_read_template(self):
        """Test coverage
        """
        with open(path_testdata + 'xml_template.txt', 'r') as f:
            template = f.read()
        # split it as in the method
        part1, sep, part2 = template.partition(self.comtoepi.template_marker)

        self.comtoepi._template_part1 = ''
        self.comtoepi.save_xml()
        # Verify that template is read correctly
        self.assertEqual(part1, self.comtoepi._template_part1)
        self.assertEqual(part2, self.comtoepi._template_part2)

    def test_save_xml(self):
        self.comtoepi.xml = [self.comtoepi.template_marker]
        with open(path_testdata + 'xml_template.txt', 'r') as f:
            template = f.read()

        # split it as in the method
        part1, sep, part2 = template.partition(
                self.comtoepi.template_marker)
        # Need to add a line to pass the test. In term of XML does not matter
        template = part1 + sep + '\n' + part2

        self.comtoepi.xml_main_file = 'test_save_xml.txt'
        self.comtoepi.save_xml()

        with open(self.comtoepi.xml_main_file, 'r') as f:
            test = f.read()

        self.assertEqual(template, test)
        os.remove(self.comtoepi.xml_main_file)

    def test_treat_footnote(self):
        self.comtoepi._footnotes = ['*1*ssss tttt ] conieci: '
                                    'aaaa bbbb L5: om. Y']
        self.comtoepi.treat_footnotes()
        self.assertIsNotNone(self.comtoepi._footnotes_app.footnotes)
        self.assertIsNotNone(self.comtoepi._footnotes_app._xml_app)

    def test_main_open_document(self):
        self.comtoepi.fname = path_testdata + 'aphorisms.txt'
        self.comtoepi.main()
        self.assertIsNotNone(self.comtoepi._text)

    def test_main_open_document_failed(self):
        self.comtoepi.fname = path_testdata + 'do not exit'
        self.assertRaises(AphorismsToXMLException, self.comtoepi.main)

    def test_main_division_failed(self):
        self.comtoepi.fname = path_testdata + 'aphorisms_failed_division.txt'
        self.assertRaises(AphorismsToXMLException, self.comtoepi.main)

    def test_main_no_point_commentaries(self):
        """test for coverage"""
        self.comtoepi.fname = (path_testdata +
                               'aphorisms_no_point_commentaries.txt')
        self.comtoepi.main()
        # self.assertRaises(AphorismsToXMLException, self.comtoepi.main)

    def test_main_references(self):
        self.comtoepi.fname = (path_testdata +
                               'aphorisms_references_failed.txt')
        self.comtoepi.main()

    # # ################# process_folder ###################
    # Moved to driver:
    # TODO: implement unittest for driver
    # def test_process_folder(self):
    #     self.comtoepi.template_folder = path_testdata
    #     self.assertTrue(self.comtoepi.process_folder(path_testdata))
    #
    # def test_process_folder_raise_error_folder_not_present(self):
    #     folder = os.path.join('path_failed')
    #     self.assertRaises(AphorismsToXMLException,
    #                       self.comtoepi.process_folder,
    #                       folder)

# if __name__ == '__main__':
#     pytest.main()
