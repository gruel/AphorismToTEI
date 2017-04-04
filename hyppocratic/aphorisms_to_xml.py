"""
This module has been written to convert transcribed commentaries from text
files to TEI compatible XML.

Funding is provided by an ERC funded project studying Arabic commentaries on
the Hippocratic Aphorisms. The Principal Investigator is Peter E. Pormann,
The University of Manchester.

It is anticipated the module will be used via the main.py module
which attempts to to process any input file or directory containing files with
a .txt extension.

Each text file base name should end in an underscore followed by a
numerical value, e.g. file_1.txt, file_2.txt, etc. The numerical value is
subsequently used when creating the title section ``<div>`` element, e.g.
``<div n="1" type="Title_section">`` for file_1.txt.

.. note::
    This is optional, by default the version is set at 1.

If processing succeeds two XML files will be created in a folder called XML.
The XML file names start with the text file base name and end in _main.xml (for
the XML files will be file_1_main.xml and file_1_app.xml.

If processing fails error messages will be saved in the hyppocratic.log file.

The commentaries should be utf-8 text files with the format as documented
in the associated documentation (docs/_build/index.html).

:Authors: Jonathan Boyle, Nicolas Gruel <nicolas.gruel@manchester.ac.uk>

:Copyright: IT Services, The University of Manchester
"""
# pylint: disable=locally-disabled, invalid-name
import os
import re

try:
    from .analysis import references, footnotes, AnalysisException
    from .introduction import Introduction
    from .title import Title
    from .footnotes import Footnotes
    from .conf import logger, TEMPLATE_FNAME, TEMPLATE_MARKER
    from .baseclass import Hyppocratic
except ImportError:
    from analysis import references, footnotes, AnalysisException
    from introduction import Introduction
    from title import Title
    from footnotes import Footnotes
    from conf import logger, TEMPLATE_FNAME, TEMPLATE_MARKER
    from baseclass import Hyppocratic


# Define an Exception
class AphorismsToXMLException(Exception):
    """Class for exception
    """
    pass


class Process(Hyppocratic):
    """Class to main hypocratic aphorism text to produce a TEI XML file.

    Attributes
    ----------
    fname : str
        Name of the file to convert.
        The text file base name is expected to end with an underscore followed
        by a numerical value, e.g. file_1.txt, file_2.txt, etc. This numerical
        value is used when creating the title section <div> element, e.g.
        <div n="1" type="Title_section"> for file_1.txt.

    folder : str, optional
        Name of the folder where are the files to convert

    doc_num : int, optional
        version of the document treated.
        Default value: 1
    """
    def __init__(self,
                 fname=None,
                 folder=None,
                 doc_num=1):

        Hyppocratic.__init__(self)
        self.folder = folder
        self.fname = fname
        self.doc_num = doc_num
        self.template_fname = TEMPLATE_FNAME
        self.template_marker = TEMPLATE_MARKER

        # Create basename file.
        if self.fname is not None:
            self.set_basename()
        else:
            self.base_name = None

        self._footnotes_app = None

        # Initialise footnote number
        self._next_footnote = 1

        # other attributes used
        self._introduction = ''
        self._title = ''
        self._aph_com = {}  # aphorism and commentaries
        self._text = ''
        self._footnotes = ''
        self._n_footnote = 1
        self._template_part1 = ''
        self._template_part2 = ''

        # Initialisation of the xml_main and xml_app list
        # They are created here and not in the __init__ to have
        # the reinitialisation where it is needed.

    def set_basename(self):
        """Method to set the basename attribute if fname is not None
        """
        self.base_name = os.path.splitext(os.path.basename(self.fname))[0]

        # Create folder for XML
        if not os.path.exists('XML'):
            os.mkdir('XML')

        # Set XML file name
        self.xml_main_file = os.path.join('XML', self.base_name + '_main.xml')
        self.xml_app_file = os.path.join('XML', self.base_name + '_app.xml')

    def open_document(self, fname=None):
        """Method to open and read the hyppocratic document.

        Parameters
        ----------
        fname : str, optional
            name of the file to analyse.

        Attributes
        ----------
        folder : str, optional
            Name of the folder where are the files to convert

        fname : str
            Name of the file to convert.
            The text file base name is expected to end with an underscore
            followed by a numerical value, e.g. file_1.txt, file_2.txt, etc.
            This numerical value is used when creating the title section
            <div> element, e.g. <div n="1" type="Title_section">
            for file_1.txt.

        text : str
            string which contains the whole file in utf-8 format.

        Raises
        ------
        AphorismsToXMLException
            if document can not be:
                - open
                - there subfolder present in the folder
                - file not treatable by the software (e.g. .DS_Store)
                - file does not exist
        """
        if fname is not None:
            self.folder, self.fname = os.path.split(fname)
            self.set_basename()

        if self.base_name is None and self.fname is not None:
            self.set_basename()

        if self.folder is None:
            self.folder = '.'

        if self.base_name is None:
            logger.error("There are no file to convert.")
            raise AphorismsToXMLException

        full_path = os.path.join(self.folder, self.fname)
        if os.path.isdir(full_path):
            logger.info('The software does not treat subfolder.')
            raise AphorismsToXMLException

        # Extract the document number, it is expected this is at the end of the
        # base name following an '_'
        try:
            sep, doc_num = self.base_name.rpartition('_')[1:]
            self.doc_num = int(doc_num)
            if sep == '':
                raise AphorismsToXMLException
        except ValueError:
            info = ('File name {} does not provide version information. '
                    'Use version 1 by default'.format(self.fname))
            logger.info(info)

        # Open the file to process
        # pylint: disable=locally-disabled, invalid-name
        try:
            with open(full_path, 'r',
                      encoding="utf-8") as f:
                # Read in file
                self._text = f.read().strip()
        except UnicodeDecodeError:
            info = ('File {} is not treatable by the software'.format(
                self.fname))
            logger.info(info)
            raise AphorismsToXMLException
        except FileNotFoundError:
            info = ('File {} does not exist'.format(self.fname))
            logger.info(info)
            raise AphorismsToXMLException

    def divide_document(self):
        """Method to divide the document in the three main parts.

        An hyppocratic document si composed in three or four main parts:

        - The introduction (optional)
        - The title
        - The aphorisms
        - The footnotes

        This method will divide the document in the three or four parts.

        Attributes
        ----------
        _introduction : str
            A string which contains the introduction of the document if present

        _title : str
            A string which contains the title of the document

        _text : str
            A string which contains the aphorisms and commentaries
            of the document

        _footnotes : str
            A string which contains the footnotes of the document

        Raises
        ------
        AphorismsToXMLException
            if it is not possible to divide the document.
        """

        # Not sure that is the best way to do but this is just a trial

        # cut the portion of the test, starting from the end, until the
        # characters footnotes_sep
        footnotes_sep = '*1*'
        loc_footnotes = self._text.rfind(footnotes_sep)

        if loc_footnotes == self._text.find(footnotes_sep):
            logger.error('Footnote referenced in the text but '
                         'no footnote section present.')
            self._footnotes = ''
            raise AphorismsToXMLException

        if loc_footnotes != -1:
            self._footnotes = self._text[loc_footnotes:].strip()
            self._text = self._text[:loc_footnotes]
        else:
            logger.info('There are no footnotes present.')

        # Cut the intro (if present)
        try:
            p = re.compile(r'\+\+\n')
            _tmp = p.split(self._text)
            if len(_tmp) == 3:
                self._title = _tmp[0].strip()
                self._introduction = _tmp[1].strip()
                self._text = _tmp[2].strip()
            elif len(_tmp) == 2:
                self._introduction = _tmp[0].strip()
                self._text = _tmp[1].strip()
        except ValueError as e:
            raise AphorismsToXMLException(e)

        try:
            p = re.compile(r'\s+1\.?\n')
            if self._title == '':
                self._title, self._text = p.split(self._text)
                self._text = '1.\n' + self._text
        except ValueError as e:
            logger.error('Aphorism should have numeration as 1. or 1')
            raise AphorismsToXMLException(e)

    #     def analysis_aphorism_dict(self, com):
#         """Create an ordered dictionary with the different witness and
#          footnotes present in a commentary
#
#         Returns
#         -------
#
#         """
#         # Find all the witnesses in the line
#         # Note on the regex:
#         #     \w = [a-AA-Z0-9_]
#         #     \s = any king of space
#         #     + = one or more
#         # It match all the witness with form like [WWWWW XXXXX]
#
#         # find all the footnote in the line
#         # It match all the footnote marker like *XXX*
#         p_foot = re.compile(r'\*\d+\*')
#         footnotes = p_foot.finditer(com)
#         footnotes = {int(i.group().strip('*')): i.span() for i in footnotes}
#
#         p_wits = re.compile(r'\[\w+\s+\w+\]')
#         # wits = p.findall(com)
#         wits = p_wits.finditer(com)
#         wits = {i.group().strip('*'): i.span() for i in wits}
#
#         return footnotes, wits, com
# #        return footnotes, wits, span_f

    def aphorisms_dict(self):
        """Create an order dictionary (OrderedDict object) with the aphorisms
        and commentaries.

        Attributes
        ----------
        _aph_com : dict
            dictionary which contains the aphorisms and the commentaries
            associated.

        Raises
        ------
        AphorismsToXMLException
            if it is not possible to create the dictionary.
        """

        # \n\d+.\n == \n[0-9]+.\n (\d == [0-9])
        aphorism = re.split(r'\s+[0-9]+\.?\n', '\n' + self._text)[1:]

        # n_aphorism = [int(i.strip('\n').strip('.')) for i in
        #               re.findall('\n[0-9]+.\n', '\n' + self.text)]

        # n_aphorism = [int(i.group().strip('\n').strip('.')) for i in
        #               re.finditer('\n[0-9]+.\n', '\n' + self.text)]

        # Split the text in function of the numbers (i.e. the separation
        # of the aphorism.
        # '\s[0-9]+.\n' means 'find string :
        #    which start with end of line or any space characer
        #    with at least on number ending
        #    with a point and a end of line.
        p = re.compile(r'\s+[0-9]+\.?\n')
        error = ''
        try:
            n_aphorism = [int(i.group().strip('.\t\n '))
                          for i in p.finditer('\n' + self._text)]
            # Find missing aphorism or badly written (e.g.: 14-)
            missing = [i for i in list(range(1, max(n_aphorism)))
                       if i not in n_aphorism]
            # Find if multiple aphorism with the same number.
            doublon = list({i for i in n_aphorism if n_aphorism.count(i) > 1})
            if not n_aphorism:
                error = 'There are no aphorisms detectec'
                logger.error(error)
            if max(n_aphorism) != len(n_aphorism):
                error = 'N aphorism expected {}, got: {}'.format(
                    n_aphorism[-1],
                    len(n_aphorism)
                )
                logger.error(error)
            if missing:
                error = 'Missing or problematic aphorism: {}'.format(missing)
                logger.error(error)
                warning = ('Last aphorism can be problematic but '
                           'not detected by the software.')
                logger.warning(warning)
            if doublon:
                error = 'Aphorism with same number: {}'.format(doublon)
                logger.error(error)
            if error:
                raise AphorismsToXMLException(error)
        except ValueError:
            error = ('Aphorism numeration format probably does not respect '
                     'the convention. '
                     'It should be a number following by a point')
            logger.error(error)
            raise AphorismsToXMLException
        except AphorismsToXMLException as e:
            raise AphorismsToXMLException(e)

        # create the dictionary with the aphorism (not sure that we need
        # the ordered one)
        # use n_aphorism to be sure that there are no error

        try:
            self._aph_com = {}
            for i, aph in enumerate(aphorism):
                self._aph_com[n_aphorism[i]] = [s.strip()
                                                for s in aph.split('\n')
                                                if len(s) != 0]
        except (IndexError, AphorismsToXMLException):
            error = ('Problem in the creation of the dictionary which'
                     'which contains the aphorisms')
            logger.error(error)
            raise AphorismsToXMLException

    def read_template(self):
        """Method to read the XML template used for the transformation

        Attributes
        ----------
        template : str
            Contain the text of the XML template provided.

        Raises
        ------
        AphorismsToXMLException
            if template cannot be found or read.
        """
        # Open the template file. Kill the process if not there.
        # Template is not optional.

        try:
            with open(self.template_fname, 'r', encoding="utf-8") as f:
                template = f.read()
                info = 'Template file {} found.'.format(self.template_fname)
                logger.info(info)
        except FileNotFoundError:
            error = 'Template file {} not found.'.format(self.template_fname)
            logger.error(error)
            raise AphorismsToXMLException

        # Split the template at template_marker
        self._template_part1, sep, self._template_part2 = template.partition(
            self.template_marker)

        # Test the split worked
        if sep == '':
            error = ('Unable to find template marker text ({}) '
                     'in the template file {}.'.format(self.template_marker,
                                                       self.template_fname))
            logger.error(error)
            raise AphorismsToXMLException

        logger.debug('Template file splitted.')

    def save_xml(self):
        """Method to save the main XML file

        Two XML files are created as result to the transformation in the EPIDOC
        format one contain the introduction, title, aphorisms and commentaries.
        The other one contains the footnotes informations.
        This method create the main one.
        """
        # Embed xml_main into the XML in the template
        if self._template_part1 == '':
            self.read_template()

        if self.xml:
            # Save main XML to file
            with open(self.xml_main_file, 'w', encoding="utf-8") as f:
                f.write(self._template_part1)
                for s in self.xml:
                    f.write(s + '\n')
                f.write(self._template_part2)

    def treat_footnotes(self):
        """Method to treat Footnote.

        Work even if division of the document didn't work properly but
        for the footnotes part.
        """
        if not self._footnotes == '':
            # In most of the file the footnote will be present and can be
            # treated independently from the aphorism.

            # Treat the footnote part and create the XML app
            self._footnotes_app = Footnotes(self._footnotes)
            logger.info('Footnotes treated')

            # Create XML app and save in a file
            self._footnotes_app.xml_app()
            logger.info('Footnotes app file created')

    def main(self):
        """
        A function to process a text file containing symbols representing
        references to witnesses and symbols and footnotes defining textual
        variations, omissions, additions, correxi or conieci. This function
        uses these symbols to produce files containing EpiDoc compatible XML.

        If processing succeeds two XML files will be created in folder ./XML
        with file names that start with the text file base name and ending in
        _main.xml (for the main XML) and _apps.xml (for the apparatus XML).
        For example for file_1.txt the XML files will be file_1_main.xml and
        file_1_app.xml.

        Modify the attribute ``xml`` to add the title section in the main XML

        Raises
        ------
        AphorismsToXMLException
            if the processing of the file does not work as expected.

        """

        # Open and read the hyppocratic document
        self.open_document()

        debug = 'Open document {}'.format(self.fname)
        logger.debug(debug)

        # Divide the document in the different part (intro, title,
        # text, footnotes)

        try:
            self.divide_document()
            logger.info('Division of the document ok.')
        except AphorismsToXMLException:
            logger.error('Division of the document failed.')
            raise AphorismsToXMLException

        self.treat_footnotes()
        self._footnotes_app.save_xml(self.xml_app_file)

        self.aphorisms_dict()
        logger.info('Created aphorisms dictionary')

        if self._introduction != '':
            intro = Introduction(self._introduction, self._next_footnote)
            intro.xml_main()
            self._next_footnote = intro.next_footnote
            self.xml += intro.xml
            logger.debug('Introduction treated')

        # Deal with the first block of text which should contain
        # an optional intro
        # and the title
        # =======================================================

        title = Title(self._title, self._next_footnote, self.doc_num)
        logger.debug('Title treated')

        title.xml_main()
        logger.debug('Title xml created')

        self._next_footnote = title.next_footnote

        # Add title to the xml main
        self.xml += title.xml

        # Now process the rest of the main text
        # =====================================
        logger.debug('Start aphorisms and commentaries treatment')
        for k in self._aph_com:
            aphorism = self._aph_com[k][0]
            commentaries = self._aph_com[k][1:]

            # Add initial XML for the aphorism + commentary unit
            self.xml.append(self.xml_oss * self.xml_n_offset + '<div n="' +
                            str(k) + '" type="aphorism_commentary_unit">')

            # Add initial XML for this aphorism
            self.xml.append(self.xml_oss * (self.xml_n_offset + 1) +
                            '<div type="aphorism">')
            self.xml.append(self.xml_oss * (self.xml_n_offset + 2) + '<p>')

            # Now process any witnesses in it. If this fails with a
            # CommentaryToEpidocException print an error and return
            try:
                line_ref = references(aphorism)
            except AnalysisException:
                error = ('Unable to process references in '
                         'aphorism {}'.format(k))
                logger.error(error)
                raise AphorismsToXMLException from None

            if line_ref is None or line_ref == '':
                continue

            # Process any footnotes in line_ref, if there are errors write
            # to the log file and return
            try:
                self.xml_n_offset += 3
                xml_main_to_add, self._next_footnote = \
                    footnotes(line_ref, self._next_footnote)
                self.xml_n_offset -= 3
            except (TypeError, AnalysisException):
                error = ('Unable to process footnotes in '
                         'aphorism {}'.format(k))
                logger.error(error)
                raise AphorismsToXMLException from None

            # Add the XML
            self.xml.extend(xml_main_to_add)

            # Close the XML for the aphorism
            self.xml.append(self.xml_oss * (self.xml_n_offset + 2) + '</p>')
            self.xml.append(self.xml_oss * (self.xml_n_offset + 1) + '</div>')

            # Get the next line of text
            for n_com, line in enumerate(commentaries):

                # Workaround footnote on first word
                line = ' ' + line

                if line[-1] != '.':

                    debug = ('Commentaries should ended with a `.`\n'
                             'Warning in aphorism {}\n'
                             'commentary {}'.format(k, line))
                    logger.debug(debug)

                # Add initial XML for this aphorism's commentary
                self.xml.append(self.xml_oss * (self.xml_n_offset + 1) +
                                '<div type="commentary">')
                self.xml.append(self.xml_oss * (self.xml_n_offset + 2) + '<p>')

                # Now process any witnesses in this line. If this fails with a
                # CommentaryToEpidocException and log an error
                try:
                    line_ref = references(line)
                except AnalysisException:
                    error = ('Unable to process _references, '
                             'commentary {} for aphorism '
                             '{}'.format(n_com+1, k))
                    logger.error(error)
                    raise AphorismsToXMLException from None

                # Process any _footnotes in line_ref. If this fails with a
                # CommentaryToEpidocException and log an error
                try:
                    self.xml_n_offset += 3
                    xml_main_to_add, self._next_footnote = \
                        footnotes(line_ref, self._next_footnote)
                    self.xml_n_offset -= 3
                except (TypeError, AnalysisException):
                    error = "Unable to process Aphorism {}".format(k)
                    logger.error(error)
                    raise AphorismsToXMLException from None

                # Add the XML
                self.xml.extend(xml_main_to_add)

                # Close the XML for this commentary
                self.xml.append(self.xml_oss * (self.xml_n_offset + 2) +
                                '</p>')
                self.xml.append(self.xml_oss * (self.xml_n_offset + 1) +
                                '</div>')

            # Close the XML for the aphorism + commentary unit
            self.xml.append(self.xml_oss * self.xml_n_offset + '</div>')

        logger.debug('Finish aphorisms and commentaries treatment')
        # Save the xmls created
        self.save_xml()
        logger.debug('Save main xml')
