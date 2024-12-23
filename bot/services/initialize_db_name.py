import sys

this = sys.modules[__name__]
this.db_name = None


def initialize_db(name):
    if this.db_name is None:
        this.db_name = name
    else:
        msg = "Database is already initialized to {0}."
        raise RuntimeError(msg.format(this.db_name))
