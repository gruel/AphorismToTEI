import logging.config

try:
    from hyppocratic.analysis import references, footnotes
except ImportError:
    from analysis import references, footnotes

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

    def __init__(self, title, doc_num, next_footnote_to_find):
        self.title = title
        self.doc_num = doc_num
        self.next_footnote_to_find = next_footnote_to_find

        self.xml = []
        self.xml_n_offset = xml_n_offset

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
                line_ref = references(line)
            except TitleException:
                error = ('Unable to process title _references '
                         'in line {} '.format(line))
                logger.error(error)
                raise TitleException

            # Process any footnotes in line_ref,
            # if this fails print to the error file and return
            try:
                self.xml_n_offset += 2
                xml_main_to_add, self.next_footnote_to_find = \
                    footnotes(line_ref, self.next_footnote_to_find)
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
