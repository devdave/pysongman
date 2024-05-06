"""
The bridge API between the python application and the TS/react frontend
"""

import logging

from .application import App

LOG = logging.getLogger(__name__)


class Logger:
    """
    A simple utility logger
    """

    __app: App

    def __init__(self, app: App):
        self.__app = app
        LOG.debug("Logger initialized")
        print(__name__)

    def info(self, message):
        """
        Info logger
        :param message:
        :return:
        """
        LOG.info(message)

    def debug(self, message):
        """
        Debug logger

        :param message:
        :return:
        """
        LOG.debug(message)

    def error(self, message):
        """
        Error logger

        :param message:
        :return:
        """
        LOG.error(message)


class API:
    """
    The actual API bridge
    """

    __app: App
    logger: Logger

    def __init__(self, app):
        self.__app = app

        self.logger = Logger(app)

    def test(self):
        print("test")
