import logging
import pathlib
import typing

import PySide2
from PySide2 import QtCore
from PySide2.QtCore import Qt
from PySide2 import QtWidgets
from PySide2 import QtMultimedia
DisplayRole = Qt.DisplayRole
ToolTipRole = Qt.ToolTipRole

import mutagen
import tinytag

from . import initialize_db
# from .base import Base
from .song import Song
from ..lib.ffprobe import FFProbe
from ..lib.song_info import SongInfo

log = logging.getLogger(__name__)




class PlaylistItem:

    @classmethod
    def Load(cls, file_path):
        data = mutagen.File(file_path)
        return cls(data, file_path)

    def __init__(self, data, file_path):
        self.data = data
        self.file_path = file_path

    def tiny_title(self):
        """
            Attempt to
        Returns:
        """
        tags = tinytag.TinyTag.get(self.file_path)
        artist = tags.artist
        title = tags.title
        if None in [artist, title]:
            # log.debug("Tiny tag ID3 lookup failed on %s", self.file_path)
            stem = pathlib.Path(self.file_path).stem
            if "-" in stem:
                artist, title = stem.split("-",1)
                return f"{artist} - {title}"
            else:
                return stem
        else:
            return f"{artist} - {title}"


    @property
    def title(self):

        artist = self.data.get("artist", [None])[0]
        title = self.data.get("title", [None])[0]
        if None in [artist, title]:
            # TODO Amazon and similar vendors like to sneak in an anti-piracy ID3 hash string which wrecks mutagen
            # try to detect if that is why there is no artist/title
            return self.tiny_title()
        else:
            return f"{artist} - {title}"



    @property
    def duration_str(self):
        duration = self.data.info.length
        seconds = int(duration % 60)
        minutes = int(duration / 60)
        return f"{minutes}:{seconds:02}"


class Table(QtCore.QAbstractTableModel):

    playlist: QtMultimedia.QMediaPlaylist
    # Signals
    media_removed = QtCore.Signal()
    media_added = QtCore.Signal()
    index_changed = QtCore.Signal(int)

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
        log.debug("index=%s", index)
        self.index_changed.emit(index)

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
        return len(self.headers)

    def headerData(self, section: int, orientation: PySide2.QtCore.Qt.Orientation, role: int = ...) -> typing.Any:
        if role == Qt.DisplayRole:
            return self.headers[section]

    def data(self, index: PySide2.QtCore.QModelIndex, role: int = ...) -> typing.Any:
        media = self.playlist.media(index.row())  # type: QtMultimedia.QMediaContent

        if role == DisplayRole:

            fetcher = self.fetchers[index.column()]
            path = media.canonicalUrl().toString()
            record = Song.GetByPath(path)
            if record is None:
                record = SongInfo(path)

            data = fetcher(record)

            return data

        elif role == ToolTipRole:
            return media.canonicalUrl().toString()






