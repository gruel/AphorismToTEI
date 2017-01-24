# Pure python dictionary with the configuration for the logging
# TODO: can be transformed in yaml file eventually

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