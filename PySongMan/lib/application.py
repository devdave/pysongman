"""
The internal application class and its dependencies
"""

import webview


class App:
    """
    The internal application instance

    """

    port: str
    __main_window: webview.Window

    def __init__(self, port="8080"):
        self.__main_window = None
        self.port = port

    @property
    def main_window(self) -> webview.Window:
        return self.__main_window

    @main_window.setter
    def main_window(self, main_window: webview.Window):
        self.__main_window = main_window
