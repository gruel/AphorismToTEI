"""Module used to treat the footnotes from the hypocratic project.

Note
----
- pylint analysis: 10

Disable two warning which I cannot avoid and are not really problematic::

    pylint --disable=R0915,R0912 footnotes.py

Authors: Jonathan Boyle, Nicolas Gruel
Copyright: IT Services, The University of Manchester
"""
import re
import logging.config
from collections import OrderedDict

try:
    from hyppocratic.conf import LOGGING
    from hyppocratic.baseclass import Hyppocratic
except ImportError:
    from conf import LOGGING
    from baseclass import Hyppocratic

# Read logging configuration and create logger
logging.config.dictConfig(LOGGING)
# pylint: disable=locally-disabled, invalid-name
logger = logging.getLogger('hyppocratic.CommentaryToEpidoc')


# Define an Exception
class FootnotesException(Exception):
    """Class for exception
    """
    pass


class Footnote(Hyppocratic):
    """Class Footnote which treat an individual footnote

    Attributes
    ----------
    self.footnote: str
        String which contains the footnote to treat.
    self.n_footnote: int
        Integer which give the reference number of the footnote treated.
    """
    def __init__(self, footnote=None, n_footnote=None):
        Hyppocratic.__init__(self)
        self.footnote = footnote
        self.n_footnote = n_footnote

        self.d_footnote = {}

    def omission(self, xml_app):
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
        2. ``*n*`` (where n is the footnote number) from the start of
           the string
        3. ``.`` character from the end of the string

        TODO: update that dosctring this is wrong

        The footnote is expected to contain a single ':' character and have the
        following format:

        1. The footnote line before the ':' character is a string of witness
           text, followed by the ']' character, followed by a single witness
           code.
        2. The footnote line after the ':' character contains an 'om.' followed
           by a single witness code.

        The second input argument should be a list containing
        the apparatus XML, this function will add XML to this list.

        The third input argument is the string defining a unit of offset in
        the XML, this defaults to four space characters.

        It is intended this function is called by _footnotes()
        for omission footnotes.
        """
        reason = None
        corr = None
        wits = [None, None]
        # Split the footnote

        try:
            # Split to get the text and remove the space
            _tmp = self.footnote.split(']')
            text = _tmp[0].strip()

            # split around om. to
            _tmp = _tmp[1].split('om.')
            wits[1] = _tmp[-1].strip()
            _tmp = _tmp[0].strip().split()

            if len(_tmp) == 1:
                wits[0] = _tmp[0].strip(':').strip()
            else:
                reason = _tmp[0].strip(':').strip()
                # join all the other element to get the full original text
                corr = ' '.join(_tmp[1:-1])
                wits[0] = _tmp[-1].strip(':').strip()
        except IndexError:
            error = 'Error in footnote: {}'.format(self.n_footnote)
            logger.error(error)
            error = 'Omission footnote error: {}'.format(self.footnote)
            logger.error(error)
            return

        self.d_footnote = {'reason': reason,
                           'text': text,
                           'witnesses': wits,
                           'corrections': corr}
        self._omission_xml(xml_app)

    def _omission_xml(self, xml_app):
        """Method to create the XML portion related to footnote (TEI format)

        Parameters
        ----------
        """
        # Add the correxi or conieci if needed
        if self.d_footnote['reason'] == 'correxi':
            # Add text xml_app
            xml_app.append(self.xml_oss + '<rdg>')
            xml_app.append(self.xml_oss * 2 + '<choice>')
            xml_app.append(self.xml_oss * 3 + '<corr>' + self.d_footnote['text']
                           + '</corr>')
            xml_app.append(self.xml_oss * 2 + '</choice>')
            xml_app.append(self.xml_oss + '</rdg>')
            self.d_footnote['text'] = self.d_footnote['corrections']
        elif self.d_footnote['reason'] == 'conieci':
            # Add text xml_app
            xml_app.append(self.xml_oss + '<rdg>')
            xml_app.append(self.xml_oss * 2 + '<choice>')
            xml_app.append(self.xml_oss * 3 + '<corr type="conjecture">' +
                           self.d_footnote['text'] + '</corr>')
            xml_app.append(self.xml_oss * 2 + '</choice>')
            xml_app.append(self.xml_oss + '</rdg>')
            self.d_footnote['text'] = self.d_footnote['corrections']
        elif self.d_footnote['reason'] is not None:
            error = 'Type of correction unexpected: ' \
                    '{}'.format(self.d_footnote['reason'])
            logger.error(error)
            raise FootnotesException

        # Add the witness to the XML (remember to strip whitespace)
        xml_app.append(self.xml_oss + '<rdg wit="#' +
                       self.d_footnote['witnesses'][0] + '">' +
                       self.d_footnote['text'] + '</rdg>')

        # Add witness to the XML
        xml_app.append(self.xml_oss + '<rdg wit="#' +
                       self.d_footnote['witnesses'][1]
                       + '">')
        xml_app.append(self.xml_oss * 2 + '<gap reason="omission"/>')
        xml_app.append(self.xml_oss + '</rdg>')

    def correction(self, reason, xml_app):
        """
        This helper function processes a footnote line describing correxi, i.e.
        corrections by the editor, these contain the string 'correxi'.

        The first input argument must be the footnote line with the following
        stripped from the start and end of the string:

        1. All whitespace
        2. ``*n*`` (where n is the footnote number) from the start of
           the string
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

        The second input argument should be a list containing
        the apparatus XML, this function will add XML to this list.

        The third input argument is a string defining the unit of offset
        for the XML, this defaults to four space characters.

        It is intended this function is called by _footnotes()
        for correxi footnotes.
        """
        corrs = [None, None]
        wits = [None, None]
        try:
            # Split to get the text, the reason and remove the space
            _tmp = self.footnote.split(']')
            text = _tmp[0].strip()
            _tmp = _tmp[1]

            if reason in ['correxi', 'conieci']:
                _tmp = _tmp.split(reason + ':')
                _tmp = _tmp[1].strip()
            elif reason == 'add':
                _tmp = _tmp.split('add.')
                _tmp = _tmp[1].strip()

            #TODO: need to implement the new form!
            if reason == 'add' and ',' not in _tmp and ':' not in _tmp:
                _tmp = _tmp.split()
                wits[0] = _tmp[-1].strip()
                corrs[0] = ' '.join(_tmp[:-1]).strip()
            elif ',' in _tmp:
                _tmp = _tmp.split(',')
                wits[1] = _tmp[-1].strip()
                _tmp = _tmp[0].split()
                wits[0] = _tmp[-1].strip()
                corrs[0] = ' '.join(_tmp[:-1])
                corrs[1] = corrs[0]
            elif ':' in _tmp:
                _tmp = _tmp.split(':')
                _tmp1 = _tmp[0].split()
                wits[0] = _tmp1[-1].strip()
                corrs[0] = ' '.join(_tmp1[:-1]).strip()

                _tmp2 = _tmp[1].split()
                wits[1] = _tmp2[-1].strip()
                corrs[1] = ' '.join(_tmp2[:-1]).strip()
            else:
                raise FootnotesException

        except (IndexError, FootnotesException):
            error = 'Error in footnote: {}'.format(self.n_footnote)
            logger.error(error)
            error = 'Footnote error: {}'.format(self.footnote)
            logger.error(error)
            return

        self.d_footnote = {'reason': reason,
                           'text': text,
                           'witnesses': wits,
                           'corrections': corrs}

        self._correction_xml(xml_app)

    def _correction_xml(self, xml_app):
        """Method to create the XML portion related to footnote (TEI format)

        Parameters
        ----------
        """
        # Add to the XML
        if self.d_footnote['reason'] == 'add':
            for i, wit in enumerate(self.d_footnote['witnesses']):
                if wit is not None:
                    xml_app.append(self.xml_oss + '<rdg wit="#' + wit + '">')
                    xml_app.append(self.xml_oss * 2 +
                                   '<add reason="add_scribe">' +
                                   self.d_footnote['corrections'][i] +
                                   '</add>')
                    xml_app.append(self.xml_oss + '</rdg>')
            return

        if self.d_footnote['reason'] == 'standard':
            self.d_footnote['corrections'][0] = self.d_footnote['text']

        if (self.d_footnote['reason'] == 'correxi' or
                self.d_footnote['reason'] == 'conieci'):

            # Add text xml_app
            xml_app.append(self.xml_oss + '<rdg>')
            xml_app.append(self.xml_oss * 2 + '<choice>')

            if self.d_footnote['reason'] == 'correxi':
                xml_app.append(self.xml_oss * 3 + '<corr>' + self.d_footnote['text']
                               + '</corr>')
            elif self.d_footnote['reason'] == 'conieci':
                xml_app.append(self.xml_oss * 3 + '<corr type="conjecture">' +
                               self.d_footnote['text'] + '</corr>')
            else:
                raise FootnotesException

            xml_app.append(self.xml_oss * 2 + '</choice>')
            xml_app.append(self.xml_oss + '</rdg>')

        for i in [0, 1]:
            xml_app.append(self.xml_oss + '<rdg wit="#' +
                           self.d_footnote['witnesses'][i] + '">' +
                           self.d_footnote['corrections'][i] + '</rdg>')


class Footnotes(object):
    """Class to analyse and create the XML app file for the entire set of
    footnotes.

    Attributes
    ----------
    self.footnotes: list, str, OrderedDict, dict
        List which contains the whole set of footnote from the hyppocratic
        file.
    """

    def __init__(self, footnotes=None):
        if isinstance(footnotes, (list, str)):
            self.footnotes = footnotes
            self._dictionary()
        elif isinstance(footnotes, (dict, OrderedDict)):
            self.footnotes = footnotes
        self._xml_app = []

    def _dictionary(self):
        """Create an ordered dictionary (OrderedDict object) with the footnotes

        Returns
        -------
        dic: OrderedDict
            contains the footnotes as an Ordered Dictionary.
            Keys are the number of the footnote (integer) and value is
            the footnote.
        """
        # Split the footnotes by lines (in theory one line per footnote)
        # pylint: disable=locally-disabled, no-member
        try:
            if isinstance(self.footnotes, str) and self.footnotes != '':
                _tmp = self.footnotes.splitlines()
            elif isinstance(self.footnotes, list):
                _tmp = self.footnotes
            elif isinstance(self.footnotes, (dict, OrderedDict)):
                return
            _size = len(_tmp)
        except UnboundLocalError:
            error = ('Attributes footnotes should be a non empty string, '
                     'a list, a dictionary or an OrderedDict '
                     'but is {}'.format(type(self.footnotes)))
            logger.error(error)
            raise FootnotesException

        # Check that the number of footnote is in agreement
        # with their numeration
        if not re.findall(str(_size), _tmp[-1])[0] == str(_size):
            error = 'Number of footnotes {} not in agreement ' \
                    'with their numeration in the file'.format(_size)
            logger.error(error)
            raise FootnotesException

        # Create the ordere dictionary and remove the '.'
        _dic = OrderedDict()
        for line in _tmp:
            try:
                key, value = line.rsplit('*')[1:]
            except ValueError:
                error = 'There are a problem in footnote: {}'.format(line)
                logger.error(error)
                raise FootnotesException

            # Remove space and '.'
            _dic[int(key)] = value.strip().strip('.')

            self.footnotes = _dic

    def xml_app(self):
        """Method to create the XML add for the footnote

        Returns
        -------
        xml_app: list
            list which contains the lines with the XML related to the footnotes
        """

        # Verify footnotes for common errors
        self._verification()

        for n_footnote in self.footnotes.keys():

            # Add initial XML to xml_app (for the apparatus XML file)
            self._xml_app.append('<app from="#begin_fn' + str(n_footnote) +
                                 '" to="#end_fn' + str(n_footnote) + '">')
            # Get the corresponding footnote (start at 1)
            footnote_line = self.footnotes[n_footnote]

            # Now process the footnote line - deal with each case individually
            # to aid readability and make future additions easier

            ft = Footnote(footnote_line, n_footnote)

            # Now process the footnote
            # Case 1 - omission
            if 'om.' in footnote_line:
                ft.omission(self._xml_app)

            # Case 2 - addition
            elif 'add.' in footnote_line:
                ft.correction('add', self._xml_app)

            # Case 3 - correxi
            elif 'correxi' in footnote_line:
                ft.correction('correxi', self._xml_app)

            # Case4 - conieci
            elif 'conieci' in footnote_line:
                ft.correction('conieci', self._xml_app)

            # Remaining case - standard variation
            else:
                ft.correction('standard', self._xml_app)

            # Close the XML
            self._xml_app.append('</app>')

    def _verification(self):
        """A function to test all footnotes have the correct format.
        The input argument should be a python list containing the footnotes.
        The function returns a python list containing the error messages.
        """
        error = ''

        # Assure that the footnotes is a dictionary or an OrderedDict
        self._dictionary()

        # Initialise list to hold error messages

        for k in self.footnotes:
            footnote = '*{}*{}.'.format(k, self.footnotes[k])
            # Discard any empty lines
            if footnote == '':
                continue

            # Test there are two '*' characters
            try:
                if footnote.count('*') != 2:
                    error = ('Error in footnote ' + str(k) +
                             ': should contain two "*" characters')
                    raise FootnotesException
            except FootnotesException:
                logger.error(error)
                error = 'Footnotes: {}'.format(footnote)
                logger.error(error)

            # Test the first character is a '*' and remove it
            try:
                if footnote[0] != '*':
                    error = ('Error in footnote ' + str(k) +
                             ': first character is not an "*"')
                    raise FootnotesException
            except FootnotesException:
                logger.error(error)
                error = 'Footnotes: {}'.format(footnote)
                logger.error(error)
            footnote = footnote.lstrip('*')

            # Test the last character is a '.'
            try:
                if footnote[-1] != '.':
                    error = ('Error in footnote ' + str(k) +
                             ': last character is not an "."')
                    raise FootnotesException
            except FootnotesException:
                logger.error(error)
                error = 'Footnotes: {}'.format(footnote)
                logger.error(error)

            # Partition at the next '*' and check the footnote number
            try:
                _tmp = footnote.partition('*')
                n = _tmp[0]
                footnote = _tmp[2]
                if int(n) != k:
                    error = ('Error in footnote ' + str(k) +
                             ': expected footnote ' +
                             str(k) + ' but found footnote ' + n)
                    raise FootnotesException
            except FootnotesException:
                logger.error(error)
                error = 'Footnotes: {}'.format(footnote)
                logger.error(error)

            # Check the footnote contains one ']'
            # we must notice that most of the editor will show
            # the opposite symbol [
            try:
                if footnote.count(']') != 1:
                    error = ('Error in footnote ' + str(k) +
                             ': should contain one "]" character')
                    raise FootnotesException
            except FootnotesException:
                logger.error(error)
                error = 'Footnotes: {}'.format(footnote)
                logger.error(error)

            # Check for known illegal characters
            # If contains a 'codd' give an error and stop further processing
            try:
                if 'codd' in footnote:
                    error = ('Error in footnote ' + str(k) +
                             ': contains "codd"')
                    raise FootnotesException
            except FootnotesException:
                logger.error(error)
                error = 'Footnotes: {}'.format(footnote)
                logger.error(error)

            # If contains a ';' give an error and stop further processing
            try:
                if ';' in footnote:
                    error = ('Error in footnote ' + str(k) +
                             ': contains ";"')
                    raise FootnotesException
            except FootnotesException:
                logger.error(error)
                error = 'Footnotes: {}'.format(footnote)
                logger.error(error)

            # Test omission has the correct format
            # Errors tested for:
            # - should not contain any ','
            if 'om.' in footnote:

                try:
                    if ',' in footnote:
                        error = ('Error in footnote ' + str(k) +
                                 ': omission should not contain "," character')
                        raise FootnotesException
                except FootnotesException:
                    logger.error(error)
                    error = 'Footnotes: {}'.format(footnote)
                    logger.error(error)

            # Test addition has the correct format
            # Errors tested for:
            #  - text after ']' should be ' add. '
            elif 'add.' in footnote:

                try:
                    part2 = footnote.partition(']')[2]
                    if part2[0:6] != ' add. ':
                        error = ('Error in footnote ' + str(k) +
                                 ': addition must contain " add. " after "]"')
                        raise FootnotesException
                except FootnotesException:
                    logger.error(error)
                    error = 'Footnotes: {}'.format(footnote)
                    logger.error(error)

            elif 'correxi' in footnote:
                pass
            elif 'conieci' in footnote:
                pass

            # Test standard variations have the correct format
            # Errors tested for:
            # - should not contain any ','
            # - should contain one ':'
            else:

                try:
                    if ',' in footnote:
                        error = ('Error in footnote ' + str(k) +
                                 ': standard variation should not contain '
                                 '"," character')
                        raise FootnotesException
                except FootnotesException:
                    logger.error(error)
                    error = 'Footnotes: {}'.format(footnote)
                    logger.error(error)

                try:
                    if footnote.count(':') != 1:
                        error = ('Error in footnote ' + str(k) +
                                 ': standard variation should contain one '
                                 '":" character')
                        raise FootnotesException
                except FootnotesException:
                    logger.error(error)
                    error = 'Footnotes: {}'.format(footnote)
                    logger.error(error)

    def save_xml(self, fname='xml_app.xml'):
        """Method to save the XML app string in a file

        Parameters
        ----------
        fname: str (optional)
            name of the file where the XML app will be saved.
        """

        with open(fname, 'w', encoding="utf-8") as f:
            for s in self._xml_app:
                f.write(s + '\n')
