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
    # Signals
    media_removed = QtCore.Signal()
    media_added = QtCore.Signal()

    def __init__(self, playlist, headers_fetchers):
        super(Table, self).__init__()
        self.playlist = playlist # type: QtMultimedia.QMediaPlaylist
        self.headers = list(headers_fetchers.keys())
        self.fetchers = list(headers_fetchers.values())

        self.playlist.mediaInserted.connect(self.on_media_inserted)
        self.playlist.mediaRemoved.connect(self.on_media_removed)
        self.playlist.currentIndexChanged.connect(self.on_index_changed)

    def on_media_inserted(self):
        self.layoutAboutToBeChanged.emit()
        self.media_added.emit()
        self.layoutChanged.emit()

    def on_media_removed(self):
        self.layoutAboutToBeChanged().emit()
        self.media_removed.emit()
        self.layoutchanged.emit()

    def on_index_changed(self, index):
        print(f"PLT: {index}")

    def select_song_by_path(self, path):
        for index in range(self.playlist.mediaCount()):
            media_url = self.playlist.media(index).canonicalUrl()
            if media_url == path:
                self.playlist.setCurrentIndex(index)


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
        if role == Qt.DisplayRole or role == Qt.ToolTipRole:

            if index.column() == 0:
                return index.row()
            else:
                fetcher = self.fetchers[index.column() - 1]
                media = self.playlist.media(index.row())  # type: QtMultimedia.QMediaContent
                path = media.canonicalUrl().toString()
                record = Song.GetByPath(path)
                if record is None:
                    record = PlaylistItem.Load(path)

                return fetcher(record)




