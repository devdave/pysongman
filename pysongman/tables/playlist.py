import logging
import typing

from .. import USE_PYSIDE

if USE_PYSIDE:
    from PySide2 import QtCore

    from pybass3.pys2_playlist import Pys2Playlist

    Qt = QtCore.Qt


log = logging.getLogger(__name__)


class PlaylistTableModel(QtCore.QAbstractTableModel):

    playlist: Pys2Playlist

    def __init__(self, playlist: Pys2Playlist):
        super(PlaylistTableModel, self).__init__()
        self.playlist = playlist

        self.playlist.song_added.connect(self.on_song_added)
        self.playlist.songs_added.connect(self.on_songs_added)

    def rowCount(self, parent: QtCore.QModelIndex = ...) -> int:
        return len(self.playlist)

    def columnCount(self, parent: QtCore.QModelIndex = ...) -> int:
        return 4

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = ...) -> typing.Any:
        if role == Qt.DisplayRole:
            if section == 0:
                return "SID"
            elif section == 1:
                return "#"
            elif section == 2:
                return "Time"
            elif section == 3:
                return "Name"

        return None

    def data(self, index: QtCore.QModelIndex, role: int = ...) -> typing.Any:

        song = self.playlist.get_song_by_row(index.row())
        col = index.column()
        if role == Qt.DisplayRole:
            if col == 0:
                return song.id
            elif col == 1:
                return index.row() + 1
            elif col == 2:
                return song.duration_time
            elif col == 3:
                return song.title

        elif role == Qt.ToolTipRole:
            if col == 2:
                return song.file_path.as_posix()

    def on_song_added(self, song_id: str):
        log.debug("Telling PL Table a new song has been added.")
        index = self.playlist.get_indexof_song_by_id(song_id)
        index_model = QtCore.QModelIndex()
        self.beginInsertRows(index_model, index, index)
        self.endInsertRows()

    def on_songs_added(self, payload):
        log.debug("Telling PL that multiple songs have been added.")
        starting_index, song_ids = payload
        index_model = QtCore.QModelIndex()

        self.beginInsertRows(index_model, starting_index+1, len(song_ids))

        self.endInsertRows()