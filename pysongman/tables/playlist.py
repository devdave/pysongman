import typing

from .. import USE_PYSIDE

if USE_PYSIDE:
    from PySide2 import QtCore

    Qt = QtCore.Qt


class PlaylistTableModel(QtCore.QAbstractTableModel):

    def __init__(self, playlist):
        super(PlaylistTableModel, self).__init__()
        self.playlist = playlist

        self.playlist.song_added.connect(self.song_added)

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

    def song_added(self, song_id: str):

        index = self.playlist.get_indexof_song_by_id(song_id)
        index_model = QtCore.QModelIndex()
        self.beginInsertRows(index_model, index, index)
        self.endInsertRows()