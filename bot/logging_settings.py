from log_filters import ExceptionLogFilter, InfoLogFilter

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
            'filename': '/app/logs/error.log',
            'level': 'ERROR',
            'formatter': 'default',
            'filters': ['exception_filter'],
            'encoding': 'utf-8'
        },
        'info_file': {
            'class': 'logging.FileHandler',
            'filename': '/app/logs/info.log',
            'level': 'INFO',
            'formatter': 'default',
            'filters': ['info_filter'],
            'encoding': 'utf-8'
        }
    },
    'loggers': {
        'get_bot': {
            'level': 'DEBUG',
            'handlers': ['error_file', 'info_file']
        },
        'handlers.message_handlers': {
            'level': 'DEBUG',
            'handlers': ['error_file', 'info_file']
        },
    },
}