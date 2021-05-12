"""
    Similar to the Playlist Table but instead shows the queue

"""

from .. import USE_PYSIDE
import typing
import logging

if USE_PYSIDE is True:
    from PySide2 import QtCore
    from PySide2.QtCore import Qt

from pybass3.pys2_playlist import Pys2Playlist

log = logging.getLogger(__name__)

class QueueTableModel(QtCore.QAbstractTableModel):

    playlist: Pys2Playlist

    def __init__(self, playlist: Pys2Playlist):
        super(QueueTableModel, self).__init__()
        log.debug("QueueTableModel initialized")

        self.playlist = playlist
        self.playlist.queue_changed.connect(self.on_queue_change)


    def columnCount(self, parent:QtCore.QModelIndex=...) -> int:
        return 4

    def rowCount(self, parent:QtCore.QModelIndex=...) -> int:
        return len(self.playlist.queue)

    def headerData(self, section:int, orientation:QtCore.Qt.Orientation, role:int=...) -> typing.Any:
        if section == 0:
            return "SID"
        elif section == 1:
            return "#"
        elif section == 2:
            return "Time"
        elif section == 3:
            return "Name"

    def data(self, index:QtCore.QModelIndex, role: int = ...) -> typing.Any:
        row = index.row()
        col = index.column()
        song = self.playlist.get_song_by_id(self.playlist.queue[row])

        if role == Qt.DisplayRole:
            if col == 0:
                return song.id
            elif col == 1:
                return row
            elif col == 2:
                song.duration_time
            elif col == 3:
                song.title
        elif role == Qt.ToolTipRole:
            if col == 3:
                return song.file_path.as_posix()


    def on_queue_change(self) -> None:
        """
            This feels a bit ridiculous

        """
        self.beginRemoveRows(QtCore.QModelIndex(), 0, self.rowCount())
        self.endRemoveRows()

        self.beginInsertRows(QtCore.QModelIndex(), 0, len(self.playlist.queue))
        self.endInsertRows()

