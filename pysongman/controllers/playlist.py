
import PySide2
from PySide2 import QtCore
from PySide2.QtCore import Qt
from PySide2 import QtWidgets

from ..views.playlist_window import PlaylistWindow
from ..models.playlist import Table as PlaylistTable


class PlaylistController(QtCore.QObject):
    def __init__(self, playlist_obj):
        super(PlaylistController, self).__init__()


        self.playlist = playlist_obj
        self.table_model = PlaylistTable(self.playlist, {"Title": lambda r: r.title, "Duration": lambda r: r.duration_ms} )

        self.setupUI()

    def setupUI(self):
        self.view = PlaylistWindow()


    def connect(self):
        pass

    def show(self):
        self.view.show()

    def hide(self):
        self.view.hide()