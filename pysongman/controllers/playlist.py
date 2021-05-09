import logging

from .. import USE_PYSIDE

if USE_PYSIDE:
    from PySide2 import QtCore
    from PySide2 import QtWidgets

    from pybass3.pys2_playlist import Pys2Playlist

from ..tables.playlist import PlaylistTableModel
from ..views.playlist_window import PlaylistWindow

log = logging.getLogger(__name__)

class Playlist(QtCore.QObject):

    playlist: Pys2Playlist
    table_model: PlaylistTableModel
    view: PlaylistWindow

    def __init__(self, playlist_obj):
        """

        Args:
            playlist_obj: A PyBass Playlist object
            playlist_tm: The Table Model for Playlist
        """
        self.playlist = playlist_obj
        self.table_model = PlaylistTableModel(playlist_obj)
        self.view = PlaylistWindow(self.playlist, self.table_model)

        self.setup_connections()

    def setup_connections(self):
        self.view.table.doubleClicked.connect(self.on_row_doubleclicked)

        self.playlist.song_changed.connect(self.on_song_changed)

    def show(self):
        self.view.show()

    def hide(self):
        self.view.hide()

    def on_row_doubleclicked(self, index: QtCore.QModelIndex):
        log.debug("on_row_doubleclicked %s clicked", index)
        self.playlist.play_song_by_index(index.row())

    def on_song_changed(self, song_id):
        log.debug("Playlist control song changed to %s", song_id)

        song_index = self.playlist.get_indexof_song_by_id(song_id)
        self.view.table.selectRow(song_index)
        self.view.table.resizeColumnsToContents()