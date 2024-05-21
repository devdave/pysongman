"""
The internal application class and its dependencies
"""

import contextlib

import webview

from . import models


class App:
    """
    The internal application instance

    """

    port: str
    __main_window: webview.Window | None
    db_path: str | None

    def __init__(self, port="8080", db_path=None):
        self.__main_window = None
        self.port = port
        self.db_path = db_path

    @property
    def main_window(self) -> webview.Window:
        return self.__main_window

    @main_window.setter
    def main_window(self, main_window: webview.Window):
        self.__main_window = main_window

    @contextlib.contextmanager
    def get_db(self):
        engine, session = models.connect(db_path=self.db_path)
        yield session
        session.close()
