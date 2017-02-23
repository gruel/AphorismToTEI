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
class IntroductionException(Exception):
    """Class for exception
    """
    pass


class Introduction(object):

    def __init__(self, introduction, next_footnote):
        self.introduction = introduction
        self.next_footnote = next_footnote

        self.xml = []
        self.xml_n_offset = xml_n_offset

    def xml_main(self):
        """Method to treat the optional part of the introduction.
        """
        introduction = self.introduction.splitlines()

        # Generate the opening XML for the intro
        self.xml.append(xml_oss * self.xml_n_offset + '<div type="intro">')
        self.xml.append(xml_oss * (self.xml_n_offset + 1) + '<p>')

        for line in introduction:
            if line == '':
                continue

            # Process any witnesses in this line. If this fails with a
            # IntroductionException print an error and return
            try:
                line_ref = references(line)
            except IntroductionException:
                error = ('Unable to process _references in the introduction'
                         ' (line: {})'.format(line))
                logger.error(error)
                raise IntroductionException

            # Process any footnotes in line_ref. If this fails with a
            # IntroductionException print an error and return
            try:
                self.xml_n_offset += 2
                xml_main_to_add, self.next_footnote = \
                    footnotes(line_ref, self.next_footnote)
                self.xml_n_offset -= 2
            except IntroductionException:
                error = ('Unable to process _references in the introduction'
                         ' (line: {})'.format(line))
                logger.error(error)
                raise IntroductionException

            # Add to the XML
            self.xml.extend(xml_main_to_add)

        # Add XML to close the intro section
        self.xml.append(xml_oss * (self.xml_n_offset + 1) + '</p>')
        self.xml.append(xml_oss * self.xml_n_offset + '</div>')