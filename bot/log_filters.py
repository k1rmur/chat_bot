import logging


class InfoLogFilter(logging.Filter):
    def filter(self, record):
        return record.levelname == "INFO"


class ExceptionLogFilter(logging.Filter):
    def filter(self, record):
        return record.levelname == "ERROR"


class UserActionLogFilter(logging.Filter):
    """Filter for user action logs only"""
    def filter(self, record):
        return record.name == "user_actions" and record.levelname == "INFO"
