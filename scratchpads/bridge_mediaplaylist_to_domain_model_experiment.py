"""
    Experiment doesn't work :(

    QT rips off the extra attributes in CustomContent and returns just a QMediaContent object
"""

import sys
import argparse
import typing
import pathlib

import PySide2
from PySide2 import QtCore
from PySide2.QtCore import Qt
from PySide2 import QtWidgets
from PySide2 import QtMultimedia

from ffprobe_analyzer import FFProbe

class MockDomain:

    data = []

    @classmethod
    def Generate(cls, song_dir):
        song_dir = pathlib.Path(song_dir)
        files = (file for file in song_dir.iterdir() if file.is_file() and file.name.endswith((".ogg", ".mp3")))
        for file in files:
            probe = FFProbe(file)
            cls.data.append(probe)

    @classmethod
    def GetByPath(cls, path):
        search_path = pathlib.Path(path)
        for record in cls.data:  # type: FFProbe
            if record.song_path == search_path:
                return record


class Playlist2Table(QtCore.QAbstractTableModel):

    playlist: QtMultimedia.QMediaPlaylist

    def __init__(self, playlist, headers_fetchers):
        super(Playlist2Table, self).__init__()
        self.playlist = playlist
        self.headers = list(headers_fetchers.keys())
        self.fetchers = list(headers_fetchers.values())

    def rowCount(self, parent: PySide2.QtCore.QModelIndex = ...) -> int:
        # print(f"rc: {self.playlist.mediaCount()=}")
        return self.playlist.mediaCount()

    def columnCount(self, parent: PySide2.QtCore.QModelIndex = ...) -> int:
        """
            Row ID, header[0], header[...]
        Args:
            parent:

        Returns:

        """
        return len(self.headers) + 1

    def headerData(self, section:int, orientation:PySide2.QtCore.Qt.Orientation, role:int=...) -> typing.Any:
        if role == Qt.DisplayRole:
            if section == 0:
                return "RID"
            else:
                return self.headers[section-1]


    def data(self, index:PySide2.QtCore.QModelIndex, role:int=...) -> typing.Any:
        if role == Qt.DisplayRole:

            if index.column() == 0:
                return index.row()
            else:
                fetcher = self.fetchers[index.column() - 1]
                media = self.playlist.media(index.row())  # type: QtMultimedia.QMediaContent
                path = media.canonicalUrl().toString()
                path = path.replace("%5C", "\\")
                record = MockDomain.GetByPath(path)
                if record is None:
                    # ruh uh
                    print("Failed to lookup path: ", path)
                return fetcher(record)




    


class BasicPlayer(QtWidgets.QWidget):

    def __init__(self, song_dir):
        super(BasicPlayer, self).__init__()

        self.player = QtMultimedia.QMediaPlayer()
        self.playlist = QtMultimedia.QMediaPlaylist()
        self.load_directory(song_dir)
        self.player.setPlaylist(self.playlist)

        self.body = QtWidgets.QVBoxLayout()

        self.play2table = Playlist2Table(self.playlist, {"Title": lambda r: r.title, "Duration": lambda r: r.duration_str})

        self.playtable = QtWidgets.QTableView()
        self.playtable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.playtable.verticalHeader().hide()
        self.playtable.horizontalHeader().hide()
        self.playtable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.playtable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.playtable.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.playtable.resizeColumnsToContents()
        self.playtable.resizeRowsToContents()

        self.playtable.setModel(self.play2table)

        self.body.addWidget(self.playtable, 1)
        self.body.setStretch(0, 1)

        # basic player controls
        self.controls = QtWidgets.QHBoxLayout()

        self.playBtn = QtWidgets.QPushButton("Play")
        self.playBtn.clicked.connect(self.on_play_click)
        
        self.stopBtn = QtWidgets.QPushButton("Stop")
        self.stopBtn.clicked.connect(self.on_stop_click)

        self.controls.addWidget(self.playBtn)
        self.controls.addWidget(self.stopBtn)

        self.body.addLayout(self.controls)


        self.setLayout(self.body)


        self.playtable.doubleClicked.connect(self.on_doubleclick)

    def on_media_error(self, error):
        print(error)
        if self.playlist.currentIndex() < self.playlist.currentIndex():
            self.playlist.next()
            self.player.play()

    # for now no controller
    def on_doubleclick(self, index: QtCore.QModelIndex):
        row = index.row()
        self.playlist.setCurrentIndex(row)
        self.player.play()

        debug = 1

    def on_play_click(self):
        self.player.play()
        
    def on_stop_click(self):
        self.player.stop()

    def load_directory(self, song_dir):
        home = pathlib.Path(song_dir)
        files = (element for element in home.iterdir() if element.is_file() and element.name.endswith(".mp3"))
        for fake_id, file in enumerate(files):
            media = QtMultimedia.QMediaContent(QtCore.QUrl(str(file)))
            self.playlist.addMedia(media)

        print(f"{self.playlist.mediaCount()}")
        MockDomain.Generate(song_dir)






def main(song_dir):

    MockDomain.Generate(song_dir)
    app = QtWidgets.QApplication(sys.argv)
    view = BasicPlayer(song_dir)

    view.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("song_dir")
    args = parser.parse_args()

    main(args.song_dir)