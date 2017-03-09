"""Module to contains the configuration of the hyppocrite softeware

TODO: can be transformed in yaml file eventually

Authors: Jonathan Boyle, Nicolas Gruel
Copyright: IT Services, The University of Manchester
"""
# pylint: disable=locally-disabled, invalid-name
import logging.config
import logging

# Pure python dictionary with the configuration for the logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'default',
            'filename': 'hyppocratic.log',
            'mode': 'w',
            'encoding': 'utf-8',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'ERROR',
            'formatter': 'default',
        }
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'DEBUG',
    },
}


# Read logging configuration and create logger
logging.config.dictConfig(LOGGING)
logger = logging.getLogger('hyppocratic')

# Some constants use in the creation of the XML
XML_N_OFFSET = 3
XML_OFFSET_SIZE = 4
XML_OSS = ' ' * XML_OFFSET_SIZE

# XML template information
TEMPLATE_FOLDER = ''
TEMPLATE_FNAME = 'xml_template.txt'
TEMPLATE_MARKER = '#INSERT#'
