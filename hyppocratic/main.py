# -*- coding: utf-8 -*-
"""Main module to treat aphorisms and convert them in XML files.

:Authors: Jonathan Boyle, Nicolas Gruel <nicolas.gruel@manchester.ac.uk>

:Copyright: IT Services, The University of Manchester
"""
import sys
import os

try:
    from docopt import docopt
except ImportError:
    print("Install docopt package: pip install docopt --user")
    sys.exit()

try:
    from hyppocratic.conf import logger
    from hyppocratic.aphorisms_to_xml import Process, \
        AphorismsToXMLException
    from hyppocratic.analysis import AnalysisException
    from hyppocratic.footnotes import FootnotesException
except ImportError:
    from conf import logger
    from aphorisms_to_xml import Process, AphorismsToXMLException
    from analysis import AnalysisException
    from footnotes import FootnotesException


def main(args=None):
    """Run AphorismsToTEI scripts to produce the TEI XML

    Command line::

        Usage:
            AphorismsToTEI <files> [--xml_template=<tmpl>]
            AphorismsToTEI -h | --help
            AphorismsToTEI --version

        Options:
            -h --help              Show this screen.
            --version              Show version.
            --xml_template=<name>  Name of the XML template

        Example:
            AphorismsToTEI TextFiles

    Raises
    ------
    SystemExit
        if the file or the folder to treat is not available.
    """

    arguments = docopt(main.__doc__, argv=args,
                       version="CommentaryToEpidoc testing version")

    # Convert docopt results in the proper variable (change type when needed)

    fname = arguments['<files>']
    template_file = arguments['--xml_template']

    # Call ArabicToXML.process_folder with the following arguments
    # 1st - the folder containing the text file
    # 2nd - the name of the XML template file
    # 3rd - the number of offsets to use when adding XML to the <body> element
    # 4th - the number of space characters to use for each XML offset

    try:
        if os.path.isdir(fname):
            directory = fname.strip(os.pathsep)
            files = os.listdir(directory)
        else:
            files, directory = [fname], ''
    except FileNotFoundError:
        error = 'Error: path {} for text files ' \
                'not found'.format(directory)
        logger.error(error)
        sys.exit()

    for fname in files:
        try:
            comtoepi = Process(fname=fname, folder=directory)
            if template_file:
                comtoepi.template_fname = template_file
            comtoepi.main()
        except (AphorismsToXMLException, FootnotesException,
                AnalysisException):
            error = 'Error: unable to process "{}", ' \
                    'see log file.'.format(fname)
            logger.error(error)

    logger.info("Finished " + logger.name)


if __name__ == '__main__':
    main()
