"""
The internal application class and its dependencies
"""

import contextlib

import webview


class App:
    """
    The internal application instance

    """

    port: str
    __main_window: webview.Window

    def __init__(self, port="8080", get_session=None):
        self.__main_window = None
        self.port = port
        self.get_session = get_session

    @property
    def main_window(self) -> webview.Window:
        return self.__main_window

    @main_window.setter
    def main_window(self, main_window: webview.Window):
        self.__main_window = main_window

    @contextlib.contextmanager
    def get_db(self):
        session = self.get_session()
        yield session
        session.close()
