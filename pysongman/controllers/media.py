from .. import USE_PYSIDE


if USE_PYSIDE is True:
    from PySide2 import QtCore, QtWidgets
    from PySide2.QtCore import Qt

    from pybass3.pys2_playlist import Pys2Playlist

from ..views.media_window import MediaWindow

class MediaController(QtCore.QObject):

    def __init__(self, playlist: Pys2Playlist):
        super(MediaController, self).__init__()

        self.playlist = playlist
        self.view = MediaWindow()

        self.setup_connections()
        self.setup_models()


    def setup_connections(self):
        pass

    def setup_models(self):
        pass

    def show(self):
        self.view.show()

    def hide(self):
        self.view.hide()

    def activate(self):
        self.view.activateWindow()

