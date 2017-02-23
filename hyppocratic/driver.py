# -*- coding: utf-8 -*-
f"""

Authors: Jonathan Boyle, Nicolas Gruel
Copyright: IT Services, The University of Manchester
"""
import sys

try:
    from docopt import docopt
except ImportError:
    print("Install docopt package: pip install docopt --user")
    sys.exit()

try:
    from hyppocratic import CommentaryToEpidoc
except ImportError:
    import CommentaryToEpidoc

# Logging

import logging.config
try:
    from hyppocratic.conf import LOGGING
except ImportError:
    from conf import LOGGING

# Read logging configuration and create logger
logging.config.dictConfig(LOGGING)
logger = logging.getLogger('hyppocratic')


def main(args=None):
    """Run CommentaryToEpidoc scripts to produce the Epidoc XML

    Usage:
        CommentaryToEpidoc <directory> [--xml_template=<tmpl>] [--offset=<n>] [--offset_size=<n>]
        CommentaryToEpidoc -h | --help
        CommentaryToEpidoc --version

    Options:
        -h --help              Show this screen.
        --version              Show version.
        --xml_template=<name>  Name of the XML template [default: xml_template.txt]
        --offset=<n>         Offsets to use when adding XML to the <body> element [default: 3]
        --offset_size=<n>      Space characters to use for each XML offset [default: 4]

    Example:
        CommentaryToEpidoc TextFiles
    TODO: add an option for the output
    """

    arguments = docopt(main.__doc__, argv=args,
                       version="CommentaryToEpidoc testing version")

    # Convert docopt results in the proper variable (change type when needed)
    directory = arguments['<directory>']
    template_file = arguments['--xml_template']
    n_offset = int(arguments['--offset'])
    offset_size = int(arguments['--offset_size'])

    # Call ArabicToXML.process_folder with the following arguments
    # 1st - the folder containing the text file
    # 2nd - the name of the XML template file
    # 3rd - the number of offsets to use when adding XML to the <body> element
    # 4th - the number of space characters to use for each XML offset

    comtoepi = CommentaryToEpidoc.Process()
    comtoepi.process_folder(directory)

    logger.info("Finished " + logger.name)


if __name__ == '__main__':
    main()
