"""
This module has been written to convert transcribed commentaries from text
files to EpiDoc compatible XML, see http://www.stoa.org/epidoc/gl/latest/
and http://sourceforge.net/p/epidoc/wiki/Home/ for more information on EpiDoc.

Funding is provided by an ERC funded project studying Arabic commentaries on
the Hippocratic Aphorisms. The Principal Investigator is Peter E. Pormann,
The University of Manchester.


It is anticipated the module will be used via the function process_text_files()
which attempts to to process any file with a .txt extension within a specified
directory. Each text file base name should end in an underscore followed by a
numerical value, e.g. file_1.txt, file_2.txt, etc. The numerical value is
subsequently used when creating the title section <div> element, e.g.
<div n="1" type="Title_section"> for file_1.txt.

If processing succeeds two XML files will be created in a folder called XML.
The XML file names start with the text file base name and end in _main.xml (for
the XML files will be file_1_main.xml and file_1_app.xml.

If processing fails error messages will be saved to a file with the .err
extension in the folder ./errors


The commentaries should be utf-8 text files with the following format.

Part 1. A main body of text consisting of:

i.  A first block of text containing an optional intro section and the title,
    if an intro section exists a line containing '++' identifies the division
    between the intro (which comes first) and the title
ii. A series of numbered aphorism/commentary pairs each consisting of:
    a. A first line containing the aphorism number, this is a numerical value
       followed by the '.' character, i.e. the string 'n.' for aphorism n.
    b. A second line containing the aphorism.
    c. Additional line containing one or more commentaries, each commentary
       on a single line.

This main body of text contains symbols referring to witnesses and footnotes
in the following formats:

i.  References to witnesses have the form [WW LL] where WW is a code to
    identify the witness document, and LL is a location in the document.
ii. Footnote references (for textual variations, omissions, additions, correxi
    or conieci) have two forms. Let tttt represent a word of text without a
    variant, vvvv represent a word of text with a variation, and *n* identify
    footnote number n. Form a. is for single word variations, and form b. for
    multiple word variations:
    a. ttt tttt *n*vvvv tttt tttt
    b. ttt tttt *n*vvvv vvvv vvvv# tttt tttt

Part 2. After the main body of text is the list of numbered and ordered
        footnotes. A footnote is a single line with the following format:

i.   The line starts with the footnote number enclosed within a pair of
     asterisks, e.g. for footnote n the line starts with string '*n*'.
ii.  The footnote contains a mix of witness text (i.e. title, aphorisms and
     commentary) and symbols devised to describe omissions, additions,
     correxi, conieci and standard variations obtained by comparing two
     witness documents.
iii. The footnote line ends with a '.' character.

The 5 footnote types should have the following formats, where n is the footnote
number, W1 and W2 are witness codes, and ssss, tttt and uuuu represent segments
of witness text:

Omissions can have three forms.
Form 1: *n*ssss ] W1: om. W2.
This means the text 'ssss' is found in witness W1 but not W2.
Form 2: *n*ssss ] correxi: ttttt W1: om. W2.
This means the text 'ssss' is found in witness W1, not W2 but the editor has
corrected this to 'ssss'.
Form 3: *n*ssss ] conieci: ttttt W1: om. W2.
This means the text 'tttt' is found in witness W1, not W2 but the editor
conjectures that this should be 'ssss'.

Additions can have three forms depending on whether the addition applies to one
or both witnesses, and for the latter case whether the addition is the same or
not for both witnesses.
Form 1: *n*ssss ] add. tttt W1.
This means both witnesses have 'ssss' and W1 adds 'tttt'.
Form 2: *n*ssss ] add. tttt W1, W2.
This means both witnesses have 'ssss', and both add 'tttt' (e.g. the editor
felt the need to omit tttt).
Form 3: *n*ssss ] add. tttt W1: uuuu W2.
This means both witnesses have 'ssss', W1 adds 'tttt' whereas W2 adds 'uuuu'.

Correxi can have two forms, depending on whether the witness texts are the same
or not.
Form 1: *n*ssss ] correxi: tttt W1, W2.
This means the text 'tttt' is found in witnesses W1 and W2, the editor has
corrected this to 'ssss'.
Form 2: *n*ssss ] correxi: tttt W1: uuuu W2.
This means the text 'tttt' is found in witness W1, whereas W2 has 'uuuu'. The
editor has corrected these to 'ssss'.

Conieci can have two forms, depending on whether the witness texts are the same
or not.
Form 1: *n*ssss ] conieci: tttt W1, W2.
This means the text 'tttt' is found in witnesses W1 and W2, the editor
conjectures that this should be 'ssss'.
Form 2: *n*ssss ] conieci: tttt W1: uuuu W2.
This means the text 'tttt' is found in witness W1, whereas W2 has 'uuuu'. The
editor conjectures that these should be 'ssss'.

Standard variations can have only one form.
Form 1: *n*ssss ] W1: tttt W2.
This means witness W1 has text 'ssss' whereas W2 has 'tttt'.


This module generates the EpiDoc XML to sit within the <body> element. A
suitable XML template file containing all other XML is also required. The
template file should contain the string '#INSERT#' at the location where
additional EpiDoc XML should be inserted, e.g.

<TEI .... >
<teiHeader>
    ....
</teiHeader>
    <text>
        <body>
#INSERT#
        </body>
    </text>
</TEI>


The XML <div> elements generated are:
 - intro (optional)
 - Title_section (numbered)
 - aphorism_commentary_unit (numbered)
 - commentary (within aphorism_commentary_unit)
 - aphorism (within aphorism_commentary_unit)

Written by Jonathan Boyle, IT Services, The University of Manchester.
"""

# Import the string and os modules
import os
import sys
import re
import logging.config

try:
    from hyppocratic.footnotes import Footnotes
except ImportError:
    from footnotes import Footnotes

try:
    from hyppocratic.title import Title
except ImportError:
    from title import Title

try:
    from hyppocratic.conf import LOGGING
except ImportError:
    from conf import LOGGING

# Read logging configuration and create logger
logging.config.dictConfig(LOGGING)
# pylint: disable=locally-disabled, invalid-name
logger = logging.getLogger('hyppocratic.CommentaryToEpidoc')


# Define an Exception
class CommentaryToEpidocException(Exception):
    """Class for exception
    """
    pass


class Process(object):
    """Class to process hypocratic aphorysm text to produce a TEI XML file.


    Attributes
    ----------

    folder: str, optional
        Name of the folder where are the files to convert

    fname: str
        Name of the file to convert.
        The text file base name is expected to end with an underscore followed
        by a numerical value, e.g. file_1.txt, file_2.txt, etc. This numerical
        value is used when creating the title section <div> element, e.g.
        <div n="1" type="Title_section"> for file_1.txt.

    template_folder: str, optional
        Name of the folder where are the XML template is located

    template_marker: str, optional
            string which will be replace in the template file.
            Default=``#INSERT#``

    template_fname: str, optional
        The name of the XML template file containing the string
        ``#INSERT#`` at the location in which to insert XML for the
        ``<body>`` element.

    n_offset: int
        The number of offsets to use when creating the XML inserted in
        the <body> element in the main XML template file.
        The default value is 0.

    offset_size: int
        The number of space characters to use for each XML offset. The
        default value is 4.

    oss: str
        string wich contains the separation for the XML file.

    basename: str

    next_footnote_to_find: int

    introduction: str

    title: str
    text: str
    footnotes: str
    n_footnote: int
    template_part1: str
    template_part2: str
    doc_num: int

    # Initialisation of the xml_main and xml_app list
    # They are created here and not in the __init__ to have
    # the reinitialisation where it is needed.
    xml_main = []
    xml_app = []

    """

    def __init__(self,
                 fname=None,
                 folder=None,
                 doc_num=None,
                 template_folder='.',
                 template_fname='xml_template.txt',
                 template_marker='#INSERT#',
                 n_offset=0,
                 offset_size=4):

        self.folder = folder
        self.fname = fname
        self.doc_num = doc_num
        self.template_folder = template_folder
        self.template_fname = template_fname
        self.n_offset = n_offset
        self.offset_size = offset_size
        self.template_marker = template_marker

        #
        self.oss = ' ' * self.offset_size

        # Create basename file.
        if self.fname is not None:
            self.setbasename()
        else:
            self.base_name = None

        # Initialise footnote number
        self.next_footnote_to_find = 1

        # other attributes used
        self.introduction = ''
        self.title = ''
        self.aph_com = {}  # aphorism and commentaries
        self.text = ''
        self.footnotes = ''
        self.n_footnote = 1
        self.template_part1 = ''
        self.template_part2 = ''

        # Initialisation of the xml_main and xml_app list
        # They are created here and not in the __init__ to have
        # the reinitialisation where it is needed.
        self.xml_main = []

    def setbasename(self):
        """Method to set the basename attribute if fname is not None
        """
        self.base_name = os.path.splitext(os.path.basename(self.fname))[0]

    def open_document(self, fname=None):
        """Method to open and read the hyppocratic document.

        Parameters
        ----------
        fname: str, optional
            name of the file to analyse.

        Attributes
        ----------
        self.folder: str, optional
            Name of the folder where are the files to convert

        self.fname: str
            Name of the file to convert.
            The text file base name is expected to end with an underscore
            followed by a numerical value, e.g. file_1.txt, file_2.txt, etc.
            This numerical value is used when creating the title section
            <div> element, e.g. <div n="1" type="Title_section"> for file_1.txt.

        self.text: str
            string which contains the whole file in utf-8 format.
        """
        if fname is not None:
            self.folder, self.fname = os.path.split(fname)
            self.setbasename()

        if self.base_name is None and self.fname is not None:
            self.setbasename()

        if self.folder is None:
            self.folder = '.'

        if self.base_name is None:
            logger.error("There are no file to convert.")
            raise CommentaryToEpidocException

        # Extract the document number, it is expected this is at the end of the
        # base name following an '_'
        if self.doc_num is None:
            try:
                sep, doc_num = self.base_name.rpartition('_')[1:]
                self.doc_num = int(doc_num)
                if len(sep) == 0:
                    raise CommentaryToEpidocException
            except ValueError:
                self.doc_num = 1
                info = ('File name {} does not provide version information. '
                        'Use version 1 by default'.format(self.fname))
                logger.info(info)

        # Open the file to process
        # pylint: disable=locally-disabled, invalid-name
        with open(os.path.join(self.folder, self.fname), 'r',
                  encoding="utf-8") as f:
            # Read in file
            self.text = f.read().strip()

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
        self.introduction: str
            A string which contains the introduction of the document if present
        self.title: str
            A string which contains the title of the document
        self.text: str
            A string which contains the aphorisms and commentaries
            of the document
        self.footnotes: str
            A string which contains the footnotes of the document
        """

        # Not sure that is the best way to do but this is just a trial

        # cut the portion of the test, starting from the end, until the
        # characters footnotes_sep
        footnotes_sep = '*1*'
        loc_footnotes = self.text.rfind(footnotes_sep)

        if loc_footnotes == self.text.find(footnotes_sep):
            logger.error('Footnote referenced in the text but '
                         'no footnote section present')
            raise CommentaryToEpidocException

        if loc_footnotes != -1:
            self.footnotes = self.text[loc_footnotes:].strip()
            self.text = self.text[:loc_footnotes]
        else:
            logger.info('There are no footnotes present.')

        # Cut the intro (if present)
        intro_sep = '++\n'
        loc_intro = self.text.find(intro_sep, 3)
        # Cut the intro (remove the '++\n' at the beginning and the end.
        if loc_intro != -1:
            self.introduction = self.text[3:loc_intro].strip()
            self.text = self.text[loc_intro+3:]
        else:
            logger.info('There are no introduction present.')

        title_sep = '1.'
        loc_title = self.text.find(title_sep)
        self.title = self.text[:loc_title].strip()
        self.text = self.text[loc_title:].strip()

#     def analysis_aphorism_dict(self, com):
#         """Create an ordered dictionary with the different witness and
#          footnotes present in a commentary
#
#         Returns
#         -------
#
#         """
#         # TODO: WIP
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
        """
        # TODO: optimise there are two times the same regex

        # \n\d+.\n == \n[0-9]+.\n (\d == [0-9])
        aphorism = re.split(r'\s+[0-9]+.\n', '\n' + self.text)[1:]
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
        p = re.compile(r'\s+[0-9]+.\n')
        n_aphorism = [int(i.group().strip('\t').strip('\n').strip().strip('.'))
                      for i in p.finditer('\n' + self.text)]

        # create the dictionary with the aphorism (not sure that we need
        # the ordered one)
        # use n_aphorism to be sure that there are no error

        try:
            self.aph_com = {}
            for i, aph in enumerate(aphorism):
                self.aph_com[n_aphorism[i]] = [s for s in aph.split('\n')
                                               if len(s) != 0]
        except (IndexError, CommentaryToEpidocException):
            error = ''
            logger.error(error)
            sys.exit(1)

    def read_template(self):
        """Method to read the XML template used for the transformation

        Attribute
        ---------

        template: str

            Contain the text of the XML template provided.

        Exception
        ---------
        SystemExit if template cannot be read.
        """
        _template = os.path.join(self.template_folder, self.template_fname)
        # Open the template file. Kill the process if not there.
        # Template is not optional.

        try:
            with open(_template, 'r', encoding="utf-8") as f:
                template = f.read()
                info = 'Template file {} found in the folder {}.'.format(
                    self.template_fname, self.folder)
                logger.info(info)
        except FileNotFoundError:
            error = 'Template file {} not found in folder {}'.format(
                self.template_fname, self.template_folder)
            logger.error(error)
            sys.exit(1)

        # Split the template at template_marker
        self.template_part1, sep, self.template_part2 = template.partition(
            self.template_marker)

        # Test the split worked
        if len(sep) == 0:
            error = ('Unable to find template marker text ({}) '
                     'in the template file {} '
                     'located in the folder {}.'.format(self.template_marker,
                                                        self.template_fname,
                                                        self.template_folder))
            logger.error(error)
            sys.exit(1)

        logger.debug('Template file splitted.')

    def save_xml(self):
        """Method to save the XML files expected

        Two XML files are created as result to the transformation in the EPIDOC
        format

        Exceptions
        ==========

        """
        # Create folder for XML
        if not os.path.exists('XML'):
            os.mkdir('XML')

        # Embed xml_main into the XML in the template
        self.read_template()

        # Set XML file names
        xml_main_file = os.path.join('XML', self.base_name + '_main.xml')
        xml_app_file = os.path.join('XML', self.base_name + '_app.xml')

        # Save main XML to file
        with open(xml_main_file, 'w', encoding="utf-8") as f:
            f.write(self.template_part1)
            for s in self.xml_main:
                f.write(s + '\n')
            f.write(self.template_part2)

        # Save app XML to file
        self.footnotes_app.save_xml(xml_app_file)

    def _introduction(self):
        """Method to treat the optional part of the introduction.
        """
        introduction = self.introduction.splitlines()

        # Generate the opening XML for the intro
        self.xml_main.append(self.oss * self.n_offset + '<div type="intro">')
        self.xml_main.append(self.oss * (self.n_offset + 1) + '<p>')

        for line in introduction:
            if line == '':
                continue

            # Process any witnesses in this line. If this fails with a
            # CommentaryToEpidocException print an error and return
            try:
                line_ref = self._references(line)
            except CommentaryToEpidocException:
                error = ('Unable to process _references in the introduction'
                         ' (line: {})'.format(line))
                logger.error(error)
                raise CommentaryToEpidocException

            # Process any footnotes in line_ref. If this fails with a
            # CommentaryToEpidocException print an error and return
            try:
                self.n_offset += 2
                xml_main_to_add = self._footnotes(line_ref)
                self.n_offset -= 2
            except CommentaryToEpidocException:
                error = ('Unable to process _references in the introduction'
                         ' (line: {})'.format(line))
                logger.error(error)
                raise CommentaryToEpidocException

            # Add to the XML
            self.xml_main.extend(xml_main_to_add)

        # Add XML to close the intro section
        self.xml_main.append(self.oss * (self.n_offset + 1) + '</p>')
        self.xml_main.append(self.oss * self.n_offset + '</div>')

    def _references(self, line):
        """
        This helper function searches a line of text for witness references
        with the form ``[WW LL]`` and returns a string containing the original
        text with each witness reference replaced with XML with the form
        ``<locus target="WW">LL</locus>``.

        ``\n`` characters are added at the start and end of each XML insertion
        so each instance of XML is on its own line.

        It is intended this function is called by function process_file()
        for each line of text from the main body of the text document before
        processing footnote references using the _footnotes() function.
        """

        # Create a string to contain the return value
        result = ''

        while True:
            # Try to partition this line at the first '[' character
            text_before, sep, text_after = line.partition('[')

            # Note: if sep is zero there are no more witnesses to add

            # Add text_before to the result string
            if len(text_before) > 0:
                result += text_before
                # If there is a witness to add start a new line
                if len(sep) > 0:
                    result += '\n'

            # If sep has zero length we can stop because there are no more
            # witness _references
            if len(sep) == 0:
                break

            # Try to split text_after at the first ']' character
            reference, sep, line = text_after.partition(']')

            # If this partition failed then something went wrong,
            # so throw an error
            if len(sep) == 0:
                logger.error('Unable to partition string at "]" '
                             'when looking for a reference')
                raise CommentaryToEpidocException

            # Partition the reference into witness and location (these are
            # separated by the ' ' character)
            witness, sep, page = reference.partition(' ')

            # If this partition failed there is an error
            if len(sep) == 0:
                error = ('Unable to partition reference {} '
                         'because missing " " '
                         'character'.format(reference))
                logger.error(error)
                raise CommentaryToEpidocException

            # Add the witness and location XML to the result string
            result += '<locus target="' + witness.strip() + \
                      '">' + page.strip() + '</locus>'

            # If text has zero length we can stop
            if len(line) == 0:
                break
            else:
                # There is more text to process so start a new line
                result += '\n'

        return result

    def _footnotes(self, string_to_process):
        """
        This helper function takes a single string containing text and
        processes any embedded footnote symbols (describing additions,
        omissions, correxi, conieci and standard textual variations)
        to generate XML. It also deals with any XML generated using
        function _references().

        The output is two lists of XML, one for the main text, the other
        for the apparatus.

        Parameters
        ----------

        string_to_process: str

            This string contains the text to be processed. This should contain
            a single line from the text file being processed, e.g. a title,
            aphorism or commentary. This string may already contain XML
            generated using the _references() function i.e. XML
            identifying witnesses with each <locus> XML on a new line.

        Returns
        -------

        1. A Python list containing XML for the main text.
        2. A Python list containing XML for the critical apparatus.
        3. The number of the next footnote to be processed when this function
           complete.

        It is intended this function is called by process_file() on each line
        of text from the main document body.
        """
        # Create lists to contain the XML
        xml_main = []

        next_footnote = self.next_footnote_to_find
        while True:
            # Use string partition to try to split this text at
            # the next footnote symbol
            footnote_symbol = '*' + str(next_footnote) + '*'
            text_before_symbol, sep, string_to_process = \
                string_to_process.partition(footnote_symbol)

            # If the partition failed sep will have zero length and the next
            # footnote is not in this line, hence we can stop
            # processing and return
            if len(sep) == 0:
                # Add text_before_symbol to the XML and stop processing
                for next_line in text_before_symbol.splitlines():
                    xml_main.append(self.oss * self.n_offset +
                                    next_line.strip())
                break

            # We know sep has non-zero length and we are dealing with
            # a footnote.
            # Now use string partition to try to split text_before_symbol
            # at a '#' character.
            next_text_for_xml, sep, base_text = \
                text_before_symbol.partition('#')

            # If the above partition failed the footnote refers
            # to a single word
            if len(sep) == 0:
                # Use rpartition to partition at the LAST space in the
                # string before the footnote symbol
                next_text_for_xml, sep, base_text = \
                    text_before_symbol.rpartition(' ')

            # Check we succeeded in partitioning the text before the footnote
            # at '#' or ' '. If we didn't there's an error.
            if len(sep) == 0:
                error = 'Unable to partition text before footnote symbol ' \
                        '{}'.format(footnote_symbol)
                logger.error(error)
                raise CommentaryToEpidocException

            # Add the next_text_for_xml to xml_main
            for next_line in next_text_for_xml.splitlines():
                xml_main.append(self.oss * self.n_offset + next_line.strip())

            # Create XML for this textural variation for xml_main
            next_string = ('<app n="' +
                           str(next_footnote) +
                           '" type="footnote" xml:id="begin_fn' +
                           str(next_footnote) +
                           '"><rdg>' +
                           base_text +
                           '</rdg><anchor xml:id="end_fn' +
                           str(next_footnote) + '"/>')

            # Add next_string to the xml_main, remember this may contain '\n'
            # characters and XML from a witness reference
            for next_line in next_string.splitlines():
                xml_main.append(self.oss * self.n_offset + next_line)

            # Close the XML for the main text
            xml_main.append(self.oss * self.n_offset + '</app>')

            # Increment the footnote number
            next_footnote += 1

            # Test to see if there is any more text to process
            if len(string_to_process) == 0:
                break

        self.next_footnote_to_find = next_footnote
        return xml_main

    def process_file(self):
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

        Error messages are saved in a file in the ./errors folder.

        After successful processing the function returns True, if an error
        is detected this function returns False.

        It is intended this function is called by process_folder().
        """

        # Open and read the hyppocratic document
        self.open_document()

        # Divide the document in the different part (intro, title,
        # text, footnotes)
        self.divide_document()

        # Initialisation of the xml_main and xml_app list
        # They are created here and not in the __init__ to have
        # the reinitialisation where it is needed.
        self.xml_main = []

        if self.introduction is not '':
            self._introduction()

        self.aphorisms_dict()

        # Treat the footnote part and create the XML app
        self.footnotes_app = Footnotes(self.footnotes)

        # Create XML app
        self.footnotes_app.xml_app()

        # Deal with the first block of text which should contain
        # an optional intro
        # and the title
        # =======================================================

        title = Title(self.title, [], self.doc_num)
        # TODO: to be removed
        title.next_footnote_to_find = self.next_footnote_to_find
        title.xml_main()

        # TODO: set properly the next_footnote. Should be modified
        self.next_footnote_to_find = title.next_footnote_to_find

        # Add title to the xml main
        self.xml_main += title.xml

        # Now process the rest of the main text
        # =====================================
        for n_aphorism in self.aph_com.keys():

            aphorism = self.aph_com[n_aphorism][0].strip()
            #commentaries = [s.strip() for s in self.aph_com[n_aphorism][1:]]
            commentaries = self.aph_com[n_aphorism][1:]

            # Add initial XML for the aphorism + commentary unit
            self.xml_main.append(self.oss * self.n_offset + '<div n="' +
                                 str(n_aphorism) +
                                 '" type="aphorism_commentary_unit">')

            # Add initial XML for this aphorism
            self.xml_main.append(self.oss * (self.n_offset + 1) +
                                 '<div type="aphorism">')
            self.xml_main.append(self.oss * (self.n_offset + 2) + '<p>')

            # Now process any witnesses in it. If this fails with a
            # CommentaryToEpidocException print an error and return
            try:
                line_ref = self._references(aphorism)
            except CommentaryToEpidocException:
                error = ('Unable to process _references in '
                         'aphorism {}'.format(n_aphorism))
                logger.error(error)
                raise CommentaryToEpidocException

            # Process any footnotes in line_ref, if there are errors write
            # to the log file and return
            try:
                self.n_offset += 3
                xml_main_to_add = self._footnotes(line_ref)
                self.n_offset -= 3

            except CommentaryToEpidocException:
                error = ('Unable to process footnotes in '
                         'aphorism {}'.format(n_aphorism))
                logger.error(error)
                raise CommentaryToEpidocException

            # Add the XML
            self.xml_main.extend(xml_main_to_add)

            # Close the XML for the aphorism
            self.xml_main.append(self.oss * (self.n_offset + 2) + '</p>')
            self.xml_main.append(self.oss * (self.n_offset + 1) + '</div>')

            # Get the next line of text

            for n_com in range(len(commentaries)):
                line = commentaries[n_com]
                if line[-1] != '.':

                    error = ('Commentaries should ended with a `.`\n'
                             'Error in aphorism {}\n'
                             'commentary {}'.format(n_aphorism, line))
                    logger.error(error)
                    raise CommentaryToEpidocException

                # Add initial XML for this aphorism's commentary
                self.xml_main.append(
                    self.oss * (self.n_offset + 1) + '<div type="commentary">')
                self.xml_main.append(self.oss * (self.n_offset + 2) + '<p>')

                # Now process any witnesses in this line. If this fails with a
                # CommentaryToEpidocException and log an error
                try:
                    line_ref = self._references(line)
                except CommentaryToEpidocException:
                    error = ('Unable to process _references,'
                             'commentary {} for aphorism '
                             '{}'.format(n_com, n_aphorism))
                    logger.error(error)
                    raise CommentaryToEpidocException

                # Process any _footnotes in line_ref. If this fails with a
                # CommentaryToEpidocException and log an error
                try:
                    self.n_offset += 3
                    xml_main_to_add = self._footnotes(line_ref)
                    self.n_offset -= 3

                except CommentaryToEpidocException:
                    error = "Unable to proceed Aphorism {} " \
                            "(see previous error message)".format(n_aphorism)
                    logger.error(error)
                    raise CommentaryToEpidocException

                # Add the XML
                self.xml_main.extend(xml_main_to_add)

                # Close the XML for this commentary
                self.xml_main.append(self.oss * (self.n_offset + 2) + '</p>')
                self.xml_main.append(self.oss * (self.n_offset + 1) + '</div>')

            # Close the XML for the aphorism + commentary unit
            self.xml_main.append(self.oss * self.n_offset + '</div>')

            # Increment the aphorism number
            n_aphorism += 1

        self.save_xml()

    def reset(self):
        """Reset some of the attributes to be use with process_folder
        """
        self.doc_num = None
        self.introduction = ''
        self.n_footnote = 1
        self.next_footnote_to_find = 1

    def process_folder(self, folder=None):
        """
        A function to process all files with the .txt extension in a directory.
        These files are expected to be utf-8 text files containing symbols
        representing references to witnesses and symbols and footnotes defining
        textual variations, omissions, additions, correxi or conieci.
        For each text file this function will attempt to use the symbols
        to produce files containing EpiDoc compatible XML.

        The text file base name is expected to end with an underscore followed
        by a numerical value, e.g. file_1.txt, file_2.txt, etc.
        This numerical value is used when creating the title section
        <div> element, e.g. <div n="1" type="Title_section"> for file_1.txt.

        If processing succeeds two XML files will be created in folder ./XML
        with file names starting with the text file base name and ending
        in _main.xml (for the main XML) and _apps.xml (for the apparatus XML).
        For example for file_1.txt the XML files will be file_1_main.xml and
        file_1_app.xml.

        Parameters
        ----------

        folder: str, optional
            The folder containing the text file
        """

        if folder is not None:
            self.folder = folder

        # Test that the working folder exists
        if not os.path.exists(self.folder):
            error = 'Error: path {} for text files ' \
                    'not found'.format(self.folder)
            logger.error(error)
            raise CommentaryToEpidocException

        files = os.listdir(self.folder)

        for fname in files:
            if fname.endswith(".txt"):
                info = 'Processing: "{}"'.format(fname)
                logger.info(info)
                try:
                    self.reset()
                    self.fname = fname
                    self.setbasename()
                    self.process_file()
                except CommentaryToEpidocException:
                    error = 'Error: unable to process "{}", ' \
                            'see log file.'.format(self.fname)
                    logger.error(error)
        return True
