import logging

LOG = logging.getLogger(__name__)

class Logger:

    def info(self, message):
        logging.info(message)

    def debug(self, message):
        logging.debug(message)

    def error(self, message):
        logging.error(message)

class API:

    logger:Logger

    def __init__(self):
        self.logger = Logger()


    def first_level(self):
        pass
