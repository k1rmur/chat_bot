import logging

class InfoLogFilter(logging.Filter):
    def filter(self, record):
        return record.levelname == 'INFO'


class ExceptionLogFilter(logging.Filter):
    def filter(self, record):
        return record.levelname == 'ERROR'