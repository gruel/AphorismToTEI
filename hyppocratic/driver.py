# -*- coding: utf-8 -*-
"""
Created on Fri Nov 13 14:14:17 2015

@author: mcbicjb2
"""
import sys

from docopt import docopt

from importlib import reload

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
        CommentaryToEpidoc <directory> [--xml_template=<tmpl>] [--offsets=<n>] [--space=<n>]
        CommentaryToEpidoc -h | --help
        CommentaryToEpidoc --version

    Options:
        -h --help              Show this screen.
        --version              Show version.
        --xml_template=<name>  Name of the XML template [default: xml_template.txt]
        --offsets=<n>          Offsets to use when adding XML to the <body> element [default: 3]
        --space=<n>            Space characters to use for each XML offset [default: 4]

    Example:
        CommentaryToEpidoc TextFiles
    TODO: add an option for the output
    """

    arguments = docopt(main.__doc__, argv=args,
                       version="CommentaryToEpidoc testing version")

    # Convert docopt results in the proper variable (change type when needed)
    directory = arguments['<directory>']
    template_file = arguments['--xml_template']
    n_offsets = int(arguments['--offsets'])
    n_space = int(arguments['--space'])

    # Call ArabicToXML.process_text_files with the following arguments
    # 1st - the folder containing the text file
    # 2nd - the name of the XML template file
    # 3rd - the number of offsets to use when adding XML to the <body> element
    # 4th - the number of space characters to use for each XML offset

    comtoepi = CommentaryToEpidoc.CommentaryToEpidoc()
    comtoepi.process_text_files(directory, template_file, n_offsets, n_space)

    logger.info("Finished "  + logger.name)

if __name__ == '__main__':
    main()
