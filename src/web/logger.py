import logging
import coloredlogs
from flask import has_request_context, request
import os
import sys
from dotenv import load_dotenv

load_dotenv(verbose=True)

PYTHON_LOG_LEVEL = os.getenv("PYTHON_LOG_LEVEL", "DEBUG")

log = logging.getLogger()
handler = logging.StreamHandler()  # sys.stderr will be used by default


class RequestFormatter(coloredlogs.ColoredFormatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
        else:
            record.url = None
            record.remote_addr = None

        return super().format(record)


formatter = RequestFormatter(
    "[%(asctime)s] %(remote_addr)s requested %(url)s %(name)-12s %(levelname)-8s %(message)s %(funcName)s %(pathname)s:%(lineno)d"  # noqa
)

handler.setFormatter(formatter)
handler.setLevel(PYTHON_LOG_LEVEL)  # Both loggers and handlers have a setLevel method
log.addHandler(handler)
log.setLevel(PYTHON_LOG_LEVEL)


# Log all uncuaght exceptions
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    log.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception
