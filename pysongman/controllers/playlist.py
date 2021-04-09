
import PySide2
from PySide2 import QtCore
from PySide2.QtCore import Qt
from PySide2 import QtWidgets

from ..views.playlist_window import PlaylistWindow


class PlaylistController(QtCore.QObject):
    def __init__(self, playlist_obj):
        super(PlaylistController, self).__init__()

        self.playlist = playlist_obj

        self.setupUI()

    def setupUI(self):
        self.view = PlaylistWindow()


    def connect(self):
        pass

    def show(self):
        self.view.show()