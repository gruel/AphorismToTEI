"""Module used to treat the footnotes from the hypocratic project.

Note
----
- pylint analysis: 10

Disable two warning which I cannot avoid and are not really problematic::

    pylint --disable=R0915,R0912 footnotes.py

Authors: Jonathan Boyle, Nicolas Gruel
Copyright: IT Services, The University of Manchester
"""
import sys
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
    def __init__(self, footnote=None, n_footnote=None, xml=[]):
        Hyppocratic.__init__(self)
        self.footnote = footnote
        self.n_footnote = n_footnote
        self.xml = xml

        self.d_footnote = {}

    def verification(self):
        """A function to test all footnotes have the correct format.
        The input argument should be a python list containing the footnotes.
        The function returns a python list containing the error messages.
        """
        logger.debug('Enter verification')
        error = ''

        # Initialise list to hold error messages

        k = self.n_footnote
        logger.error('verif 1: ' + str(k))
        logger.error('verif 2: ' + self.footnote)

        try:
            footnote = '*{}*{}.'.format(k, self.footnote)
        except TypeError:
            error = 'Footnote {}'.format(k)
            logger.error(error)
            raise FootnotesException

        # Test there are two '*' characters
        try:
            if footnote.count('*') != 2:
                error = ('Error in footnote {}'
                         ': should contain two "*" characters'.format(k))
                raise FootnotesException
        except FootnotesException:
            logger.error(error)
            error = 'Footnote {}: {}'.format(k, footnote)
            logger.error(error)

        # Test the first character is a '*' and remove it
        try:
            if footnote[0] != '*':
                error = ('Error in footnote ' + str(k) +
                         ': first character is not an "*"')
                raise FootnotesException
        except FootnotesException:
            logger.error(error)
            error = 'Footnote {}: {}'.format(k, footnote)
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
            error = 'Footnote {}: {}'.format(k, footnote)
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
            error = 'Footnote {}: {}'.format(k, footnote)
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
            error = 'Footnote {}: {}'.format(k, footnote)
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
            error = 'Footnote {}: {}'.format(k, footnote)
            logger.error(error)

        # If contains a ';' give an error and stop further processing
        try:
            if ';' in footnote:
                error = ('Error in footnote ' + str(k) +
                         ': contains ";"')
                raise FootnotesException
        except FootnotesException:
            logger.error(error)
            error = 'Footnote {}: {}'.format(k, footnote)
            logger.error(error)

        if 'om.' in footnote:
            pass

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
                error = 'Footnote {}: {}'.format(k, footnote)
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
                if footnote.count(':') != 1:
                    error = ('Error in footnote ' + str(k) +
                             ': standard variation should contain one '
                             '":" character')
                    raise FootnotesException
            except FootnotesException:
                logger.error(error)
                error = 'Footnote {}: {}'.format(k, footnote)
                logger.error(error)
        logger.debug('End verification')

    def omission(self):
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
        logger.debug('Enter omission')
        reason = None
        corr = None
        wits = [None, None]
        omission = [None, None]

        # Split the footnote
        try:
            # Split to get the text and remove the space
            _tmp = self.footnote.split(']')
            if len(_tmp) != 2:
                raise FootnotesException
            text = _tmp[0].strip()

            # Split the left over in function of the space
            # (after removing the trailing space)
            _tmp = _tmp[1].strip().split(' ')
            if len(_tmp) == 3:
                # form: ssss ] correxi: om. W1
                # form: ssss ] conieci: om. W1
                if _tmp[0] == 'correxi:' or _tmp[0] == 'conieci:':
                    reason = _tmp[0].strip(':')
                    wits[0] = _tmp[-1]
                    omission[0] = 'omission'
                # form: W1: om. W2
                else:
                    wits[0] = _tmp[0].strip(':')
                    wits[1] = _tmp[-1]
                    omission[1] = 'omission'
            # form: correxi: om. W1, W2
            # form: conieci: om. W1, W2
            elif len(_tmp) == 4:
                reason = _tmp[0].strip(':').strip()
                wits[0] = _tmp[-2].strip(',')
                wits[1] = _tmp[-1]
                omission = ['omission', 'omission']
            # form: ssss ] correxi: tttt W1: om. W2
            # form: ssss ] conieci: tttt W1: om. W2
            else:
                reason = _tmp[0].strip(':').strip()
                try:
                    om_index = _tmp.index('om.')
                except ValueError:
                    error = 'Missing space in footnote {}: {}'.format(
                        self.n_footnote, self.footnote)
                    logger.error(error)
                    self.d_footnote = {'note': self.footnote}

                    return
                # join all the other element to get the full original text
                corr = ' '.join(_tmp[1:om_index-1])
                wits[0] = _tmp[om_index-1].strip(':').strip()
                wits[1] = _tmp[-1]
                omission[1] = 'omission'
            self.d_footnote = {'reason': reason,
                               'text': text,
                               'witnesses': wits,
                               'corrections': corr,
                               'omission': omission}
        except (IndexError, FootnotesException):
            self.note_xml(self.footnote)
            logger.debug(self.xml)
            error = 'Omission error in footnote {}: {}'.format(self.n_footnote,
                                                               self.footnote)
            logger.error(error)

        self._omission_xml()
        logger.debug('End omission')

    def _omission_xml(self):
        """Method to create the XML portion related to footnote (TEI format)

        Parameters
        ----------
        xml_app: list
            this is an intent (in/out)
        """
        logger.debug('Enter _omission_xml')
        # Add the correxi or conieci if needed
        if self.d_footnote['reason'] == 'correxi':
            # Add text self.xml
            self.xml.append(self.xml_oss + '<rdg>')
            self.xml.append(self.xml_oss * 2 + '<choice>')
            self.xml.append(self.xml_oss * 3 + '<corr>' + self.d_footnote['text']
                           + '</corr>')
            self.xml.append(self.xml_oss * 2 + '</choice>')
            self.xml.append(self.xml_oss + '</rdg>')
            self.d_footnote['text'] = self.d_footnote['corrections']
        elif self.d_footnote['reason'] == 'conieci':
            # Add text self.xml
            self.xml.append(self.xml_oss + '<rdg>')
            self.xml.append(self.xml_oss * 2 + '<choice>')
            self.xml.append(self.xml_oss * 3 + '<corr type="conjecture">' +
                           self.d_footnote['text'] + '</corr>')
            self.xml.append(self.xml_oss * 2 + '</choice>')
            self.xml.append(self.xml_oss + '</rdg>')
            self.d_footnote['text'] = self.d_footnote['corrections']
        elif self.d_footnote['reason'] is not None:
            self.note_xml(self.footnote)
            error = 'Type of correction unexpected: ' \
                    '{} in Footnote {}: {}'.format(self.d_footnote['reason'],
                                                   self.n_footnote,
                                                   self.footnote)
            logger.error(error)
            return

        # Add the witness to the XML (remember to strip whitespace)
        for i, w in enumerate(self.d_footnote['witnesses']):
            if w is not None:
                _str = self.xml_oss + '<rdg wit="#' + w + '">'
                if self.d_footnote['omission'][i]:
                    _str += '\n' + self.xml_oss * 2 + '<gap reason="omission"/>'
                if i == 0 and self.d_footnote['text'] is not None:
                    _str += self.d_footnote['text'] + '</rdg>'
                else:
                    _str += '\n' + self.xml_oss + '</rdg>'
                self.xml.append(_str)
        logger.debug('End _omission_xml')

    def correction(self, reason):
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
        logger.debug('Enter correction')
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

            c1 = _tmp.split(':')
            d1 = c1[0].split(',')
            e1 = d1[0].split()
            corr1 = ' '.join(e1[:-1])
            wits1 = [d1[0].split()[-1]] + d1[1:]
            try:
                d2 = c1[1].split(',')
                e2 = d2[0].split()
                corr2 = ' '.join(e2[:-1])
                wits2 = [e2[-1]] + d2[1:]
            except IndexError:
                corr2 = ''
                wits2 = []

            self.d_footnote = {'reason': reason,
                               'text': text,
                               'witnesses': [wits1, wits2],
                               'corrections': [corr1, corr2]}

            if self.d_footnote['reason'] == 'standard':
                self.d_footnote['corrections'][0] = self.d_footnote['text']

        except (IndexError, FootnotesException):
            self.note_xml(self.footnote)
            error = 'Error in footnote: {}'.format(self.n_footnote)
            logger.error(error)
            error = 'Footnote error: {}'.format(self.footnote)
            logger.error(error)

        self._correction_xml()
        logger.debug('End correction')

    def _correction_xml(self):
        """Method to create the XML portion related to footnote (TEI format)

        Parameters
        ----------
        """
        logger.debug('Enter _correction_xml')
        # Add to the XML
        if self.d_footnote['reason'] == 'add':
            for i, wit in enumerate(self.d_footnote['witnesses']):
                if len(wit) != 0:
                    for w in wit:
                        self.xml.append(self.xml_oss + '<rdg wit="#' +
                                       w.strip() + '">')
                        self.xml.append(self.xml_oss * 2 +
                                       '<add reason="add_scribe">' +
                                       self.d_footnote['corrections'][i] +
                                       '</add>')
                        self.xml.append(self.xml_oss + '</rdg>')
            return

        if (self.d_footnote['reason'] == 'correxi' or
                self.d_footnote['reason'] == 'conieci'):

            # Add text self.xml
            self.xml.append(self.xml_oss + '<rdg>')
            self.xml.append(self.xml_oss * 2 + '<choice>')

            if self.d_footnote['reason'] == 'correxi':
                self.xml.append(self.xml_oss * 3 + '<corr>' +
                               self.d_footnote['text']
                               + '</corr>')
            elif self.d_footnote['reason'] == 'conieci':
                self.xml.append(self.xml_oss * 3 + '<corr type="conjecture">' +
                               self.d_footnote['text'] + '</corr>')
            else:
                self.note_xml(self.footnote, self.xml)
                raise FootnotesException

            self.xml.append(self.xml_oss * 2 + '</choice>')
            self.xml.append(self.xml_oss + '</rdg>')

        for i in range(len(self.d_footnote['witnesses'])):
            for w in self.d_footnote['witnesses'][i]:
                self.xml.append(self.xml_oss + '<rdg wit="#' + w.strip() + '">' +
                               self.d_footnote['corrections'][i] + '</rdg>')

        logger.debug('End _correction_xml')


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
        try:
            if not re.findall(str(_size), _tmp[-1])[0] == str(_size):
                raise FootnotesException
        except (IndexError, FootnotesException):
            error = 'Number of footnotes {} not in agreement ' \
                    'with their numeration in the file'.format(_size)
            logger.error(error)
            error = 'Footnote should be written on only one line.'
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
            _dic[int(key)] = value.strip('. ')

            self.footnotes = _dic

    def xml_app(self):
        """Method to create the XML add for the footnote

        Returns
        -------
        xml_app: list
            list which contains the lines with the XML related to the footnotes
        """
        for n_footnote in self.footnotes.keys():

            # Get the corresponding footnote (start at 1)
            footnote_line = self.footnotes[n_footnote]

            # Now process the footnote line - deal with each case individually
            # to aid readability and make future additions easier

            ft = Footnote(footnote_line, n_footnote, xml=[])
            # TODO: Create a return or an error to catch to save automatically in note
            ft.verification()

            # Add initial XML to xml_app (for the apparatus XML file)
            self._xml_app.append('<app from="#begin_fn' + str(n_footnote) +
                                 '" to="#end_fn' + str(n_footnote) + '">')

            self.debug(str(n_footnote) + footnote_line)
            # Now process the footnote
            # Case 1 - omission
            if 'om.' in footnote_line:
                ft.omission()

            # Case 2 - addition
            elif 'add.' in footnote_line:
                ft.correction('add')

            # Case 3 - correxi
            elif 'correxi' in footnote_line:
                ft.correction('correxi')

            # Case4 - conieci
            elif 'conieci' in footnote_line:
                ft.correction('conieci')

            # Remaining case - standard variation
            else:
                ft.correction('standard')

            self._xml_app += ft.xml
            # Close the XML
            self._xml_app.append('</app>')

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
