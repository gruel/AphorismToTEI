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
the main XML) and _apps.xml (for the apparatus XML). For example for file_1.txt
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

Omissions can have only one form.
Form 1: *n*ssss ] W1: om. W2.
This means the text 'ssss' is found in witness W1 but not W2.

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
import logging.config

try:
    from hyppocratic.conf import LOGGING
except ImportError:
    from conf import LOGGING

# Read logging configuration and create logger
logging.config.dictConfig(LOGGING)
logger = logging.getLogger('hyppocratic.CommentaryToEpidoc')


# Define an Exception
class CommentaryToEpidocException(Exception):
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
    """

    def __init__(self,
                 folder=None,
                 fname=None,
                 template_folder='.',
                 template_fname='xml_template.txt',
                 template_marker='#INSERT#',
                 n_offset=0,
                 offset_size=4):

        self.folder = folder
        self.fname = fname
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

        # Initialisation of the xml_main and xml_app list
        # They are created here and not in the __init__ to have
        # the reinitialisation where it is needed.
        self.xml_main = []
        self.xml_app = []

    def setbasename(self):
        """Method to set the basename attribute if fname is not None
        """
        logger.error('setbasename =' +self.fname)
        self.base_name = os.path.splitext(os.path.basename(self.fname))[0]

    def open_document(self):
        """Method to open and read the hyppocratic document.

        """
        if self.base_name is None and self.fname is not None:
            self.setbasename()

        if self.base_name is None:
            logger.error("There are no file to treat.")
            raise CommentaryToEpidocException

        # TODO: file name format is too strict. Relax it.
        # Extract the document number, it is expected this is at the end of the
        # base name following an '_'
        junk, sep, doc_num = self.base_name.rpartition('_')
        try:
            self.doc_num = int(doc_num)
            if len(sep) == 0:
                raise CommentaryToEpidocException
        except ValueError:
            error = ('File name {} has incorrect format'.format(self.fname))
            logger.error(error)
            raise CommentaryToEpidocException

        # Open the file to process
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

        Attribute
        ---------
        document : dict

            A dictionary which will contains the different parts of
            the document.
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
            self.footnotes = ''
            logger.info('There are no footnotes present.'.format(self.fname))

        # Cut the intro (if present)
        intro_sep = '++\n'
        loc_intro = self.text.find(intro_sep, 3)
        # Cut the intro (remove the '++\n' at the beginning and the end.
        if loc_intro != -1:
            self.introduction = self.text[3:loc_intro].strip()
            self.text = self.text[loc_intro+3:]
        else:
            self.introduction = ''
            logger.info('There are no introduction present.'.format(self.fname))

        title_sep = '1.'
        loc_title = self.text.find(title_sep)
        self.title = self.text[:loc_title].strip()
        self.text = self.text[loc_title:].strip()

    def read_template(self):
        """Method to read the XML template used for the transformation

        Attributes
        ==========

        template: str
            Contain the text of the XML template provided.

        Exceptions
        ==========
        SystemExit if template cannot be read.
        """
        _template = os.path.join(self.template_folder, self.template_fname)
        # Open the template file. Kill the process if not there.
        # Template is not optional.

        try:
            with open(_template, 'r', encoding="utf-8") as f:
                template = f.read()
                logger.info('Template file {} found '
                            'in the folder {}.'.format(self.fname,
                                                       self.folder))
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
                     'located in the folder'.format(self.template_marker,
                                                    self.template_fname,
                                                    self.template_folder))
            logger.error(error)
            sys.exit(1)

        logger.info('Template file splitted.')

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
        with open(xml_app_file, 'w', encoding="utf-8") as f:
            for s in self.xml_app:
                f.write(s + '\n')

    def _introduction(self):
        """Method to treat the optional part of the introduction.


        """
        next_line_to_process = 0
        introduction = self.introduction.splitlines()

        # TODO: Add the final character used to test the end of the introduction by Jonathan TO BE REMOVED
        introduction.append('\n++')

        # Generate the opening XML for the intro
        self.xml_main.append(self.oss * self.n_offset + '<div type="intro">')
        self.xml_main.append(self.oss * (self.n_offset + 1) + '<p>')

        # Get the next line of text
        line, next_line_to_process = \
            self.get_next_non_empty_line(introduction,
                                         next_line_to_process)

        # Loop over lines of text containing the intro
        process_more_intro = True

        while process_more_intro:

            # Process any witnesses in this line. If this fails with a
            # CommentaryToEpidocException print an error and return
            try:
                line_ref = self._references(line)
            except CommentaryToEpidocException as err:
                error = ('Unable to process _references in line {}'
                         ' (document intro)'.format(next_line_to_process))
                logger.error(error)
                error = 'Error message: {}'.format(err)
                logger.error(error)
                raise CommentaryToEpidocException

            # Process any footnotes in line_ref. If this fails with a
            # CommentaryToEpidocException print an error and return
            try:
                self.n_offset += 2
                xml_main_to_add, xml_app_to_add = self._footnotes(line_ref)
                self.n_offset -= 2
            except CommentaryToEpidocException as err:
                error = ('Unable to process _references in line {}'
                         ' (document intro)'.format(next_line_to_process))
                logger.error(error)
                error = 'Error message: {}'.format(err)
                logger.error(error)
                raise CommentaryToEpidocException

            # Add to the XML
            self.xml_main.extend(xml_main_to_add)
            self.xml_app.extend(xml_app_to_add)

            # Get the next line and test if we have reached the end of
            #  the intro
            line, next_line_to_process = \
                self.get_next_non_empty_line(introduction,
                                             next_line_to_process)
            if '++' == line:
                process_more_intro = False

        # Add XML to close the intro section
        self.xml_main.append(self.oss * (self.n_offset + 1) + '</p>')
        self.xml_main.append(self.oss * self.n_offset + '</div>')

    def _title(self):
        """Method to treat the title

        """
        # TODO: clean this function.
        self.title += '\n1.' # Add artificially the characters which stop the function
        self.title = self.title.splitlines()

        next_line_to_process = 0
        next_footnote_to_find = 1

        # Now process the title
        # ---------------------

        # Generate the opening XML for the title
        self.xml_main.append(self.oss * self.n_offset +
                             '<div n="{}" type="Title_section">'.format(
                              self.doc_num))
        self.xml_main.append(self.oss * (self.n_offset + 1) + '<ab>')

        # Get the first non-empty line of text
        line, next_line_to_process = \
            self.get_next_non_empty_line(self.title, next_line_to_process)

        # Loop over the lines in the title
        process_more_title = True

        while process_more_title:

            # Process any witnesses in this line.
            # If this raises an exception then print an error message and return
            try:
                line_ref = self._references(line)
            except CommentaryToEpidocException as err:
                error = ('Unable to process _references in line {} '
                         '(title line)'.format(next_line_to_process))
                logger.error(error)
                error = 'Error message: {}'.format(err)
                logger.error(error)
                raise CommentaryToEpidocException

            # Process any footnotes in line_ref,
            # if this fails print to the error file and return
            try:
                self.n_offset += 2
                xml_main_to_add, xml_app_to_add = \
                    self._footnotes(line_ref)
                self.n_offset -= 2
            except CommentaryToEpidocException as err:
                error = ('Unable to process _footnotes in line {} '
                         '(title line)'.format(next_line_to_process))
                logger.error(error)
                error = 'Error message: {}'.format(err)
                logger.error(error)
                raise CommentaryToEpidocException

            # Add the return values to the XML lists
            self.xml_main.extend(xml_main_to_add)
            self.xml_app.extend(xml_app_to_add)

            # Get the next line of text
            line, next_line_to_process = \
                self.get_next_non_empty_line(self.title,
                                             next_line_to_process)

            # Test if we have reached the first aphorism
            if line == '1.':
                process_more_title = False

        # Close the XML for the title
        self.xml_main.append(self.oss * (self.n_offset + 1) + '</ab>')
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
                logger.error('Unable to partition reference {} '
                             'because missing " " '
                             'character'.format(reference))
                raise CommentaryToEpidocException

            # Add the witness and location XML to the result string
            result += '<locus target="' + witness + '">' + page + '</locus>'

            # If text has zero length we can stop
            if len(line) == 0:
                break
            else:
                # There is more text to process so start a new line
                result += '\n'

        return result

    def _omission(self, footnote, xml_app):
        """Helper function processes a footnote line describing an omission

        This helper function processes a footnote line describing an omission,
        i.e. footnotes which contain the string ``om.``.

        The textual variation MUST include only only two witnesses,
        hence omissions with two witnesses are not allowed since it would make
        no sense for both witnesses to omit the same text. Therefore
        the following should be true:

        1. The footnote line contains one colon character.
        2. The footnote line doesn't contain commas.

        The first input argument must be the footnote line with the following
        stripped from the start and end of the string:

        1. All whitespace
        2. ``*n*`` (where n is the footnote number) from the start of the string
        3. ``.`` character from the end of the string

        The footnote is expected to contain a single ':' character and have the
        following format:

        1. The footnote line before the ':' character is a string of witness
           text, followed by the ']' character, followed by a single witness
           code.
        2. The footnote line after the ':' character contains an 'om.' followed
           by a single witness code.

        The second input argument should be a list containing the apparatus XML,
        this function will add XML to this list.

        The third input argument is the string defining a unit of offset in
        the XML, this defaults to four space characters.

        It is intended this function is called by _footnotes()
        for omission footnotes.
        """

        # Partition the footnote line at ':'
        part1, sep, part2 = footnote.partition(':')

        # Partition part1 at ']'
        text, sep, wit = part1.partition(']')

        # Remove whitespace from text
        text = text.strip()

        # Add the witness to the XML (remember to strip whitespace)
        xml_app.append(self.oss + '<rdg wit="#' + wit.strip() + '">' + text +
                       '</rdg>')

        # Partition part2 at 'om.' to extract witness
        junk, sep, wit = part2.partition('om.')

        # Add witness to the XML
        xml_app.append(self.oss + '<rdg wit="#' + wit.strip() + '">')
        xml_app.append(self.oss * 2 + '<gap reason="omission"/>')
        xml_app.append(self.oss + '</rdg>')

    def _addition(self, footnote, xml_app):
        """
        This helper function processes a footnote line describing an addition,
        i.e. footnotes containing the string 'add.'

        The textual variation must include only only two witnesses, however
        additions with two witnesses are are allowed, and this function will
        work with multiple witnesses.

        The first input argument must be the footnote line with the following
        stripped from the start and end of the string:

        1. All whitespace
        2. ``*n*`` (where n is the footnote number) from the start of the string
        3. ``.`` character from the end of the string

        The footnote is expected to include the string ``add.``. The text
        after ``add.`` should have one of the following formats:

        1. the witness text followed by a space and a single witness code
        2. the witness text followed by a space and multiple witnesses
           codes separated by commas
        3. multiple pairs of witness text + witness code, each pair separated
           by a ``:`` character

        The text before the string ``add`` is not important for this function.

        The second input argument should be a list containing the apparatus XML,
        this function will add XML to this list.

        The third input argument is the string defining the unit of offset
        for the XML, this default to four space characters.

        It is intended this function is called by _footnotes()
        for addition footnotes.
        """

        # Partition the footnote line at add.
        junk, sep, part2 = footnote.partition('add.')

        # Now process part2, which could have one of two formats
        # 1. Multiple text/witness pairs, each separated by :
        # 2. Single text and one or more witness(es), multiple witnesses are
        #    separated by ','

        # Deal with case 1
        if ':' in part2:
            # Split part2 at ':' (remove whitespace first)
            part2 = part2.strip().split(':')

            for variant in part2:
                # Strip whitespace and partition at last ' '
                text, sep, wit = variant.strip().rpartition(' ')

                # Add to the XML
                xml_app.append(self.oss + '<rdg wit="#' + wit + '">')
                xml_app.append(self.oss * 2 + '<add reason="add_scribe">' +
                               text.strip() + '</add>')
                xml_app.append(self.oss + '</rdg>')

        else:
            # Deal with case 2
            wits = []
            text = part2

            # First deal with sources after ',' by partitioning at last comma
            while ',' in text:
                text, sep, wit = text.rpartition(',')
                wits.append(wit.strip())

            # Partition at last ' '
            text, sep, wit = text.rpartition(' ')
            wits.append(wit)

            # Add the witness XML
            for wit in wits:
                xml_app.append(self.oss + '<rdg wit="#' + wit + '">')
                xml_app.append(self.oss * 2 + '<add reason="add_scribe">' +
                               text.strip() + '</add>')
                xml_app.append(self.oss + '</rdg>')

    def _correxi(self, footnote, xml_app):
        """
        This helper function processes a footnote line describing correxi, i.e.
        corrections by the editor, these contain the string 'correxi'.

        The first input argument must be the footnote line with the following
        stripped from the start and end of the string:

        1. All whitespace
        2. ``*n*`` (where n is the footnote number) from the start of the string
        3. ``.`` character from the end of the string

        The footnote is expected to contain at least one ``:`` character and
        have the following format:

        1. The footnote line before the first ``:`` character contains a string
           of witness text, followed by a ``]`` character.

        2. The footnote line after the ':' character has one of two formats:

            a. multiple pairs of witness text + witness code, each pair
               separated by a ``:`` character

            b. a single witness text followed by a space and a list of comma
               separated witness codes

        The second input argument should be a list containing the apparatus XML,
        this function will add XML to this list.

        The third input argument is a string defining the unit of offset
        for the XML, this defaults to four space characters.

        It is intended this function is called by _footnotes()
        for correxi footnotes.
        """

        # Partition at first ':'
        part1, sep, part2 = footnote.partition(':')

        # Partition part 1 at ']'
        text, sep, junk = part1.partition(']')

        # Add text xml_app
        xml_app.append(self.oss + '<rdg>')
        xml_app.append(self.oss * 2 + '<choice>')
        xml_app.append(self.oss * 3 + '<corr>' + text.strip() + '</corr>')
        xml_app.append(self.oss * 2 + '</choice>')
        xml_app.append(self.oss + '</rdg>')

        # Now process part2, which could have one of two formats
        # 1. Multiple text/witness pairs, each separated by :
        # 2. Single text and witness(es), multiple witnesses are separated
        #    by ','

        # Deal with case 1
        if ':' in part2:
            # Split part2 at ':' (remove whitespace first)
            variants = part2.strip().split(':')

            for var in variants:
                # Strip whitespace and partition at last ' '
                text, sep, wit = var.strip().rpartition(' ')

                # Add to the XML
                xml_app.append(self.oss + '<rdg wit="#' + wit + '">' +
                               text + '</rdg>')

        else:
            # Deal with case 2
            wits = []
            text = part2

            # First deal with sources after ','
            while ',' in text:
                text, sep, wit = text.rpartition(',')
                wits.append(wit.strip())

            # Partition at last ' '
            text, sep, wit = text.rpartition(' ')
            wits.append(wit)

            # Add the witness XML
            for wit in wits:
                xml_app.append(self.oss + '<rdg wit="#' + wit + '">' +
                               text.strip() + '</rdg>')

    def _conieci(self, footnote, xml_app):
        """
        This helper function processes a footnote line describing a _conieci,
        i.e. conjectures by the editor, these contain the string '_conieci'.

        The first input argument is the footnote line with following stripped
        from the start and end of the string:

        1. All whitespace
        2. ``*n*`` (where n is the footnote number) from the start of the string
        3. ``.`` character from the end of the string

        The footnote is expected to contain at least one ``:`` character and
        have the following format:

        1. The footnote line before the first ``:`` character contains a string
           of witness text followed by a ``]`` character.
        2. The footnote line after the ``:`` character has one of two formats:
            a. multiple pairs of variant + witness, each separated by the ``:``
               character
            b. a single variant followed by a space and a list of comma
            separated witnesses

        The second input argument should be a list containing the apparatus XML,
        this function will add XML to this list.

        The third input argument is the string defining a unit of offset
        for the XML, this defaults to four space characters.

        It is intended this function is called by _footnotes()
        for _conieci _footnotes.
        """

        # Partition at first ':'
        part1, sep, part2 = footnote.partition(':')

        # Partition part 1 at ']'
        text, sep, junk = part1.partition(']')

        # Add text xml_app
        xml_app.append(self.oss + '<rdg>')
        xml_app.append(self.oss * 2 + '<choice>')
        xml_app.append(self.oss * 3 + '<corr type="conjecture">'
                       + text.strip() + '</corr>')
        xml_app.append(self.oss * 2 + '</choice>')
        xml_app.append(self.oss + '</rdg>')

        # Now process part 2, which could have one of two formats
        # 1. Multiple variants/witnesses separated by :
        # 2. Single textual variant and witnesses separated by ','

        # Deal with case 1
        if ':' in part2:
            # Split part2 at ':' (remove whitespace first)
            lvar = part2.strip().split(':')

            for var in lvar:
                # Strip whitespace and partition at last ' '
                text, sep, wit = var.strip().rpartition(' ')

                # Add to the XML
                xml_app.append(self.oss + '<rdg wit="#' + wit + '">' + text +
                               '</rdg>')

        else:
            # Deal with case 2
            wits = []
            text = part2

            # First deal with sources after ','
            while ',' in text:
                text, sep, wit = text.rpartition(',')
                wits.append(wit.strip())

            # Partition at last ' '
            text, sep, wit = text.rpartition(' ')
            wits.append(wit)

            # Add the witness XML
            for wit in wits:
                xml_app.append(self.oss + '<rdg wit="#' + wit + '">' +
                               text.strip() + '</rdg>')

    def _standard_variant(self, footnote, xml_app):
        """
        This helper function processes a footnote line describing a standard
        textual variation, i.e. not an _omission, _addition, _correxi or
         _conieci.

        The textual variation MUST include only only two witnesses, hence
        the following should be true:

        1. The footnote line should contain one colon character.
        2. The footnote line should not contain commas.

        The first input argument is the footnote line with the following
        stripped from the start and end of the string:

        1. All whitespace
        2. ``*n*`` (where n is the footnote number) from the start of the string
        3. ``.`` character from the end of the string

        The footnote is expected to contain one ':' character and have
        the following format:

        1. Before the colon is witness text, followed by a ']' character,
           followed by a witness code.
        2. After the colon is witness text, followed by a final space character,
           followed by a witnesses code.

        The second input argument should be a list containing the apparatus XML,
        this function will add XML to this list.

        The third input argument is the string defining a unit of offset
        for the XML, this defaults to four space characters.

        It is intended this function is called by _footnotes()
        for _footnotes describing standard variations.
        """

        # Split this footnote line at the ':' character
        part1, sep, part2 = footnote.partition(':')

        # Split part 1 at the ']' character to separate the text
        # from the witness
        text, sep, wits = part1.partition(']')

        # Remove whitespace from text
        text = text.strip()

        # Add the single witness to the XML (remember to strip whitespace)
        xml_app.append(
            self.oss + '<rdg wit="#' + wits.strip() + '">' + text.strip() +
            '</rdg>')

        # Process the single witness by partitioning part2 at last ' '
        text, sep, wit = part2.rpartition(' ')

        # Add the single witness to the XML (remember to strip whitespace)
        xml_app.append(self.oss + '<rdg wit="#' + wit + '">' + text.strip() +
                       '</rdg>')

    def _footnotes(self, string_to_process):
        """
        This helper function takes a single string containing text and
        processes any embedded footnote symbols (describing additions,
        omissions, correxi, conieci and standard textual variations)
        to generate XML. It also deals with any XML generated using
        function _references().

        The output is two lists of XML, one for the main text, the other for the
        apparatus.

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
        xml_app = []

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

            # If the above partition failed the footnote refers to a single word
            if len(sep) == 0:
                # Use rpartition to partition at the LAST space in the
                # string before the footnote symbol
                next_text_for_xml, sep, base_text = \
                    text_before_symbol.rpartition(' ')

            # Check we succeeded in partitioning the text before the footnote
            # at '#' or ' '. If we didn't there's an error.
            if len(sep) == 0:
                logger.error('Unable to partition text before footnote symbol '
                             '{}'.format(footnote_symbol))
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

            # Add initial XML to xml_app (for the apparatus XML file)
            xml_app.append('<app> from="#begin_fn' + str(next_footnote) +
                           '" to="#end_fn' + str(next_footnote) + '">')

            # Get the corresponding footnote
            footnote_line = self.footnotes[next_footnote - 1]

            # Use rstrip to remove whitespace and the '.' character from the end
            # of the footnote string
            footnote_line = footnote_line.rstrip(' .')

            # Use partition to remove the footnote symbol from the start of
            # footnote_line
            junk, sep, footnote_line = footnote_line.partition(footnote_symbol)

            # Now process the footnote line - deal with each case individually
            # to aid readability and make future additions easier
            processed = False

            # Now process the footnote

            # Case 1 - omission
            if not processed and 'om.' in footnote_line:
                self._omission(footnote_line, xml_app)
                processed = True

            # Case 2 - addition
            if not processed and 'add.' in footnote_line:
                self._addition(footnote_line, xml_app)
                processed = True

            # Case 3 - correxi
            if not processed and 'correxi' in footnote_line:
                self._correxi(footnote_line, xml_app)
                processed = True

            # Case 4 - conieci
            if not processed and 'conieci' in footnote_line:
                self._conieci(footnote_line, xml_app)
                processed = True

            # Remaining case - standard variation
            if not processed:
                self._standard_variant(footnote_line, xml_app)
                # processed = True

            # Close the XML
            xml_app.append('</app>')

            # Increment the footnote number
            next_footnote += 1

            # Test to see if there is any more text to process
            if len(string_to_process) == 0:
                break

        self.next_footnote_to_find = next_footnote
        return xml_main, xml_app

    def get_next_non_empty_line(self, text, next_line_to_process=0):
        """
        A helper function to get the next non-empty line in a list of strings,
        i.e. a function to bypass empty lines.

        Parameters
        ----------

        text: list
            a list containing the lines of text

        next_line_to_process: int
            location in list to start looking for next empty line

        Returns
        -------

        1. The first non-empty line found
        2. The next location in the list to look for a non-empty line
        """

        while True:

            # Get next line and remove whitespace
            line = text[next_line_to_process].strip()

            # Ignore empty lines
            if len(line) == 0:
                next_line_to_process += 1
            else:
                break

        next_line_to_process += 1
        return line, next_line_to_process

    def verification_footnotes(self):
        """
        A function to test all footnotes have the correct format.
        The input argument should be a python list containing the footnotes.
        The function returns a python list containing the error messages.
        """

        # Initialise n_footnote
        n_footnote = 1

        # Initialise list to hold error messages

        for footnote in self.footnotes:

            # Strip any whitespace
            footnote = footnote.strip()

            # Discard any empty lines
            if len(footnote) == 0:
                continue

            # Test there are two '*' characters
            try:
                if footnote.count('*') != 2:
                    error = ('Error in footnote ' + str(n_footnote) +
                             ': should contain two "*" characters')
                    raise CommentaryToEpidocException
            except CommentaryToEpidocException:
                logger.error(error)

            # Test the first character is a '*' and remove it
            try:
                if footnote[0] != '*':
                    error = ('Error in footnote ' + str(n_footnote) +
                             ': first character is not an "*"')
                    raise CommentaryToEpidocException
            except CommentaryToEpidocException:
                logger.error(error)
            footnote = footnote.lstrip('*')

            # Test the last character is a '.'
            try:
                if footnote[-1] != '.':
                    error = ('Error in footnote ' + str(n_footnote) +
                             ': last character is not an "."')
                    raise CommentaryToEpidocException
            except CommentaryToEpidocException:
                logger.error(error)

            # Partition at the next '*' and check the footnote number
            try:
                n, sep, footnote = footnote.partition('*')
                if int(n) != n_footnote:
                    error = ('Error in footnote ' + str(n_footnote) +
                             ': expected footnote ' +
                             str(n_footnote) + ' but found footnote ' + n)
                    raise CommentaryToEpidocException
            except CommentaryToEpidocException:
                logger.error(error)

            # Check the footnote contains one ']'
            # we must notice that most of the editor will show
            # the opposite symbol [
            try:
                if footnote.count(']') != 1:
                    error = ('Error in footnote ' + str(n_footnote) +
                             ': should contain one "]" character')
                    raise CommentaryToEpidocException
            except CommentaryToEpidocException:
                logger.error(error)

            # Check for known illegal characters
            # If contains a 'codd' give an error and stop further processing
            try:
                if 'codd' in footnote:
                    error = ('Error in footnote ' + str(n_footnote) +
                             ': contains "codd"')
                    raise CommentaryToEpidocException
            except CommentaryToEpidocException:
                logger.error(error)

            # If contains a ';' give an error and stop further processing
            try:
                if ';' in footnote:
                    error = ('Error in footnote ' + str(n_footnote) +
                             ': contains ";"')
                    raise CommentaryToEpidocException
            except CommentaryToEpidocException:
                logger.error(error)

            # Test omission has the correct format
            # Errors tested for:
            # - should not contain any ','
            # - should contain one ':'
            # - text after ':' should be ' om. '
            if 'om.' in footnote:

                try:
                    if ',' in footnote:
                        error = ('Error in footnote ' + str(n_footnote) +
                                 ': omission should not contain "," character')
                        raise CommentaryToEpidocException
                except CommentaryToEpidocException:
                    logger.error(error)

                try:
                    if footnote.count(':') != 1:
                        error = ('Error in footnote ' + str(n_footnote) +
                                 ': omission should contain one ":" character')
                        raise CommentaryToEpidocException
                except CommentaryToEpidocException:
                    logger.error(error)

                try:
                    part1, sep, part2 = footnote.partition(':')
                    if part2[0:5] != ' om. ':
                        error = ('Error in footnote ' + str(n_footnote) +
                                 ': omission must contain " om. " after ":"')
                        raise CommentaryToEpidocException
                except CommentaryToEpidocException:
                    logger.error(error)

            # Test addition has the correct format
            # Errors tested for:
            #  - text after ']' should be ' add. '
            elif 'add.' in footnote:

                try:
                    part1, sep, part2 = footnote.partition(']')
                    if part2[0:6] != ' add. ':
                        error = ('Error in footnote ' + str(n_footnote) +
                                 ': addition must contain " add. " after "]"')
                        raise CommentaryToEpidocException
                except CommentaryToEpidocException:
                    logger.error(error)

            # Test correxi have the correct format
            # Errors tested for:
            # - text after ']' should be ' correxi: '
            elif 'correxi' in footnote:

                try:
                    # Partition at ']'
                    part1, sep, part2 = footnote.partition(']')

                    if part2[0:10] != ' correxi: ':
                        error = ('Error in footnote ' + str(n_footnote) +
                                 ': correxi must contain " correxi: " '
                                 'after "]"')
                        raise CommentaryToEpidocException
                except CommentaryToEpidocException:
                    logger.error(error)

            # Test conieci have the correct format
            # Errors tested for:
            # - text after ']' should be ' conieci: '
            elif 'conieci' in footnote:

                try:
                    # Partition at ']'
                    part1, sep, part2 = footnote.partition(']')

                    if part2[0:10] != ' conieci: ':
                        error = ('Error in footnote ' + str(n_footnote) +
                                 ': conieci must contain " conieci: " '
                                 'after "]"')
                        raise CommentaryToEpidocException
                except CommentaryToEpidocException:
                    logger.error(error)

            # Test standard variations have the correct format
            # Errors tested for:
            # - should not contain any ','
            # - should contain one ':'
            else:

                try:
                    if ',' in footnote:
                        error = ('Error in footnote ' + str(n_footnote) +
                                 ': standard variation should not contain '
                                 '"," character')
                        raise CommentaryToEpidocException
                except CommentaryToEpidocException:
                    logger.error(error)

                try:
                    if footnote.count(':') != 1:
                        error = ('Error in footnote ' + str(n_footnote) +
                                 ': standard variation should contain one '
                                 '":" character')
                        raise CommentaryToEpidocException
                except CommentaryToEpidocException:
                    logger.error(error)

            # Increment footnote number
            n_footnote += 1

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

        # Initialise footnote number
        self.next_footnote_to_find = 1

        # Initialise number of the next line of text to process
        # (Python indexing starts at 0)
        next_line_to_process = 0

        # Open and read the hyppocratic document
        self.open_document()

        # Divide the document in the different part (intro, title,
        # text, footnotes)
        self.divide_document()

        # Initialisation of the xml_main and xml_app list
        # They are created here and not in the __init__ to have
        # the reinitialisation where it is needed.
        self.xml_main = []
        self.xml_app = []

        logger.info('Treat the introduction if present.')
        if self.introduction is not '':
            self._introduction()

        main_text = self.text.splitlines()
        self.footnotes = self.footnotes.splitlines()

        # TODO: The test is useless as the result are not used anywhere
        # Test the footnotes
        self.verification_footnotes()

        # Deal with the first block of text which should contain
        # an optional intro
        # and the title
        # =======================================================
        self._title()

        # Now process the rest of the main text
        # =====================================

        line, next_line_to_process = \
            self.get_next_non_empty_line(main_text, next_line_to_process)

        # Initialise n_aphorism
        n_aphorism = 1

        while next_line_to_process < len(main_text):

            # Check the text in this line contains the correct aphorism number
            # If it doesn't print a message and stop
            if line[:-1] != str(n_aphorism):
                error = ('Unable to find expected aphorism number ({}) '
                         'in line {}'.format(n_aphorism,
                                             next_line_to_process))
                logger.error(error)
                error = ('Instead line {} contains the value: '
                         '{}'.format(next_line_to_process - 1, line[:-1]))
                logger.error(error)
                raise CommentaryToEpidocException

            # Add initial XML for the aphorism + commentary unit
            self.xml_main.append(self.oss * self.n_offset + '<div n="' +
                                 str(n_aphorism) +
                                 '" type="aphorism_commentary_unit">')

            # Add initial XML for this aphorism
            self.xml_main.append(self.oss * (self.n_offset + 1) +
                                 '<div type="aphorism">')
            self.xml_main.append(self.oss * (self.n_offset + 2) + '<p>')

            # Get the next line of text
            line, next_line_to_process = \
                self.get_next_non_empty_line(main_text, next_line_to_process)

            # Now process any witnesses in it. If this fails with a
            # CommentaryToEpidocException print an error and return
            try:
                line_ref = self._references(line)
            except CommentaryToEpidocException as err:
                error = ('Unable to process _references in line {} '
                         '(aphorism {})'.format(next_line_to_process,
                                                n_aphorism))
                logger.error(error)
                error = 'Error message: {}'.format(err)
                logger.error(error)
                raise CommentaryToEpidocException

            # Process any footnotes in line_ref, if there are errors write
            # to the log file and return
            try:
                self.n_offset += 3
                xml_main_to_add, xml_app_to_add = self._footnotes(line_ref)
                self.n_offset -= 3

            except CommentaryToEpidocException as err:
                error = ('Unable to process _footnotes in line {} '
                         '(aphorism {})'.format(next_line_to_process,
                                                n_aphorism))
                logger.error(error)
                error = 'Error message: {}'.format(err)
                logger.error(error)
                raise CommentaryToEpidocException

            # Add the XML
            self.xml_main.extend(xml_main_to_add)
            self.xml_app.extend(xml_app_to_add)

            # Close the XML for the aphorism
            self.xml_main.append(self.oss * (self.n_offset + 2) + '</p>')
            self.xml_main.append(self.oss * (self.n_offset + 1) + '</div>')

            # Get the next line of text
            line, next_line_to_process = \
                self.get_next_non_empty_line(main_text, next_line_to_process)

            # Now loop over commentaries
            process_more_commentary = True

            while process_more_commentary:

                # Add initial XML for this aphorism's commentary
                self.xml_main.append(
                    self.oss * (self.n_offset + 1) + '<div type="commentary">')
                self.xml_main.append(self.oss * (self.n_offset + 2) + '<p>')

                # Now process any witnesses in this line. If this fails with a
                # CommentaryToEpidocException and log an error
                try:
                    line_ref = self._references(line)
                except CommentaryToEpidocException as err:
                    error = ('Unable to process _references in line {} '
                             '(commentary for aphorism '
                             '{})'.format(next_line_to_process, n_aphorism))
                    logger.error(error)
                    error = 'Error message: {}'.format(err)
                    logger.error(error)
                    raise CommentaryToEpidocException

                # Process any _footnotes in line_ref. If this fails with a
                # CommentaryToEpidocException and log an error
                try:
                    self.n_offset += 3
                    xml_main_to_add, xml_app_to_add = self._footnotes(line_ref)
                    self.n_offset -= 3

                except CommentaryToEpidocException as err:
                    error = ('Unable to process _footnotes in line {}'
                             ' (commentary for aphorism '
                             '{})'.format(next_line_to_process, n_aphorism))
                    logger.error(error)
                    error = 'Error message: {}'.format(err)
                    logger.error(error)
                    raise CommentaryToEpidocException

                # Add the XML
                self.xml_main.extend(xml_main_to_add)
                self.xml_app.extend(xml_app_to_add)

                # Close the XML for this commentary
                self.xml_main.append(self.oss * (self.n_offset + 2) + '</p>')
                self.xml_main.append(self.oss * (self.n_offset + 1) + '</div>')

                # If there are more lines to process then get the next line and
                # test if we have reached the next aphorism
                if next_line_to_process < len(main_text):
                    line, next_line_to_process = \
                        self.get_next_non_empty_line(main_text,
                                                     next_line_to_process)
                    if line[:-1].isdigit():
                        process_more_commentary = False
                else:
                    break

            # Close the XML for the aphorism + commentary unit
            self.xml_main.append(self.oss * self.n_offset + '</div>')

            # Increment the aphorism number
            n_aphorism += 1

        self.save_xml()

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

        If processing fails error messages will be saved to a file with the .err
        extension in the folder ./errors

        Parameters
        ----------

        folder: str, optional
            The folder containing the text file
        """

        if folder is not None:
            self.folder = folder

        # Test that the working folder exists
        if not os.path.exists(self.folder):
            logger.error('Error: path {} for text files '
                         'not found'.format(self.folder))
            raise CommentaryToEpidocException

        files = os.listdir(self.folder)

        for fname in files:
            if fname.endswith(".txt"):
                logger.info('Processing: "{}"'.format(fname))
                try:
                    self.fname = fname
                    self.setbasename()
                    self.process_file()
                except CommentaryToEpidocException:
                    logger.error('Error: unable to process "{}", '
                                 'see log file.'.format(self.fname))
        return True
