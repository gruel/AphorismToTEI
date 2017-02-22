
import logging.config

try:
    from hyppocratic.conf import LOGGING, xml_oss, xml_n_offset
except ImportError:
    from conf import LOGGING, xml_oss, xml_n_offset

# Read logging configuration and create logger
logging.config.dictConfig(LOGGING)
# pylint: disable=locally-disabled, invalid-name
logger = logging.getLogger('hyppocratic.CommentaryToEpidoc')


# Define an Exception
class TitleException(Exception):
    """Class for exception
    """
    pass


class Title(object):

    def __init__(self, title, xml, doc_num):
        self.title = title
        self.xml = xml
        self.doc_num = doc_num
        self.xml_n_offset = xml_n_offset
        self.next_footnote_to_find = 1

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
                raise TitleException

            # Partition the reference into witness and location (these are
            # separated by the ' ' character)
            witness, sep, page = reference.partition(' ')

            # If this partition failed there is an error
            if len(sep) == 0:
                error = ('Unable to partition reference {} '
                         'because missing " " '
                         'character'.format(reference))
                logger.error(error)
                raise TitleException

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
                    xml_main.append(xml_oss * self.xml_n_offset +
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
                raise TitleException

            # Add the next_text_for_xml to xml_main
            for next_line in next_text_for_xml.splitlines():
                xml_main.append(xml_oss * self.xml_n_offset + next_line.strip())

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
                xml_main.append(xml_oss * self.xml_n_offset + next_line)

            # Close the XML for the main text
            xml_main.append(xml_oss * self.xml_n_offset + '</app>')

            # Increment the footnote number
            next_footnote += 1

            # Test to see if there is any more text to process
            if len(string_to_process) == 0:
                break

        self.next_footnote_to_find = next_footnote
        return xml_main

    def xml_main(self):
        """Method to treat the title

        """
        self.title = self.title.splitlines()

        # Now process the title
        # ---------------------

        # Generate the opening XML for the title
        self.xml.append(xml_oss * self.xml_n_offset +
                        '<div n="{}" '
                        'type="Title_section">'.format(self.doc_num))
        self.xml.append(xml_oss * (self.xml_n_offset + 1) + '<ab>')

        for line in self.title:

            # Process any witnesses in this line.
            # If this raises an exception then print an error message
            # and return
            try:
                line_ref = self._references(line)
            except TitleException:
                error = ('Unable to process title _references '
                         'in line {} '.format(line))
                logger.error(error)
                raise TitleException

            # Process any footnotes in line_ref,
            # if this fails print to the error file and return
            try:
                self.xml_n_offset += 2
                xml_main_to_add = \
                    self._footnotes(line_ref)
                self.xml_n_offset -= 2
            except TitleException:
                error = ('Unable to process title _references '
                         'in line {} '.format(line))
                logger.error(error)
                raise TitleException

            # Add the return values to the XML lists
            self.xml.extend(xml_main_to_add)

        # Close the XML for the title
        self.xml.append(xml_oss * (self.xml_n_offset + 1) + '</ab>')
        self.xml.append(xml_oss * self.xml_n_offset + '</div>')
