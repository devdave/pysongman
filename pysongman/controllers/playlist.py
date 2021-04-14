
import PySide2
from PySide2 import QtCore
from PySide2.QtCore import Qt
from PySide2 import QtWidgets
from PySide2 import QtMultimedia

from ..views.playlist_window import PlaylistWindow
from ..models.playlist import Table as PlaylistTable


class PlaylistController(QtCore.QObject):

    song_selected = QtCore.Signal(QtMultimedia.QMediaContent)


    def __init__(self, playlist_obj: QtMultimedia.QMediaPlaylist):
        super(PlaylistController, self).__init__()


        self.playlist = playlist_obj
        self.table_model = PlaylistTable(self.playlist, {"Title": lambda r: r.title, "Duration": lambda r: r.duration_str} )

        self.setupUI()
        self.connect()

    def setupUI(self):
        self.view = PlaylistWindow()


    def connect(self):
        self.view.table.setModel(self.table_model)
        self.view.table.doubleClicked.connect(self.on_dbl_click)

    def on_dbl_click(self, index):
        print(f"PLC: {index=}")
        # ARGH
        print(f"PLC: dbl click {index=}")
        # TODO this will be problematic later when I want to sort the playlist
        self.playlist.media(index.row())
        self.playlist.setCurrentIndex(index.row())
        media = self.playlist.currentMedia()
        self.song_selected.emit(media)




    def show(self):
        self.view.show()

    def hide(self):
        self.view.hide()