from log_filters import InfoLogFilter, ExceptionLogFilter


logging_config = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'default': {
            'format': '#%(levelname)-8s [%(asctime)s] - %(message)s'
        }
    },
    'filters': {
        'exception_filter': {
            '()': ExceptionLogFilter,
        },
        'info_filter': {
            '()': InfoLogFilter,
        },
    },
    'handlers': {
        'default': {
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        },
        'error_file': {
            'class': 'logging.FileHandler',
            'filename': 'error.log',
            'mode': 'a',
            'level': 'ERROR',
            'filters': ['exception_filter']
        },
        'info_file': {
            'class': 'logging.FileHandler',
            'filename': 'info.log',
            'mode': 'a',
            'filters': ['info_filter']
        }
    },
    'loggers': {
        'get_bot': {
            'handlers': ['error_file', 'info_file']
        }
    },
    'root': {
        'formatter': 'default',
        'handlers': ['default']
    }
}