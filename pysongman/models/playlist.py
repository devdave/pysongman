import typing

import PySide2
from PySide2 import QtCore
from PySide2.QtCore import Qt
from PySide2 import QtMultimedia

from . import initialize_db
from .base import Base
from .song import Song
from ..lib.ffprobe import FFProbe


class PlaylistItem:

    @classmethod
    def Load(cls, file_path):
        return cls(FFProbe.Load(file_path))

    def __init__(self, probed: FFProbe):
        self.probed = probed

    @property
    def title(self):
        return self.probed.listing

    @property
    def duration_str(self):
        return self.probed.duration_str

class Table(QtCore.QAbstractTableModel):


    playlist: QtMultimedia.QMediaPlaylist

    def __init__(self, playlist, headers_fetchers):
        super(Table, self).__init__()
        self.playlist = playlist
        self.headers = list(headers_fetchers.keys())
        self.fetchers = list(headers_fetchers.values())

    def rowCount(self, parent: PySide2.QtCore.QModelIndex = ...) -> int:
        return self.playlist.mediaCount()

    def columnCount(self, parent: PySide2.QtCore.QModelIndex = ...) -> int:
        """
            Row ID, header[0], header[...]
        Args:
            parent:

        Returns:

        """
        return len(self.headers) + 1

    def headerData(self, section: int, orientation: PySide2.QtCore.Qt.Orientation, role: int = ...) -> typing.Any:
        if role == Qt.DisplayRole:
            if section == 0:
                return "RID"
            else:
                return self.headers[section - 1]

    def data(self, index: PySide2.QtCore.QModelIndex, role: int = ...) -> typing.Any:
        if role == Qt.DisplayRole:

            if index.column() == 0:
                return index.row()
            else:
                fetcher = self.fetchers[index.column() - 1]
                media = self.playlist.media(index.row())  # type: QtMultimedia.QMediaContent
                path = media.canonicalUrl().toString()
                record = Domain.GetByPath(path)
                if record is None:
                    # ruh uh
                    print("Failed to lookup path: ", path)
                return fetcher(record)


