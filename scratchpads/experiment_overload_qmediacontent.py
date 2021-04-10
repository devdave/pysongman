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



class Playlist2Table(QtCore.QAbstractTableModel):

    playlist: QtMultimedia.QMediaPlaylist

    def __init__(self, playlist, domain, headers, fetchers):
        super(Playlist2Table, self).__init__()
        self.playlist = playlist
        self.domain = domain
        self.headers = headers
        self.fetchers = fetchers

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

    def headerData(self, section:int, orientation:PySide2.QtCore.Qt.Orientation, role:int=...) -> typing.Any:
        if role == Qt.DisplayRole:
            if section == 0:
                return "RID"
            else:
                return self.headers[1+section]


    def data(self, index:PySide2.QtCore.QModelIndex, role:int=...) -> typing.Any:
        if role == Qt.DisplayRole:
            media = self.playlist.media(index.row()) # type: CustomContent
            path = media.canonicalUrl().toString()
            record = self.domain.GetByPath(path)
            if record is None:
                # ruh uh
                print("Failed to lookup path: ", path)

            if index.column() == 0:
                return media.record_id
            else:
                return media.canonicalUrl().toString()




    


class BasicPlayer(QtWidgets.QWidget):

    def __init__(self):
        super(BasicPlayer, self).__init__()

        self.player = QtMultimedia.QMediaPlayer()
        self.playlist = QtMultimedia.QMediaPlaylist()
        self.player.setPlaylist(self.playlist)

        self.body = QtWidgets.QVBoxLayout()
        self.play2table = Playlist2Table(self.playlist)
        self.playtable = QtWidgets.QTableView()
        self.playtable.setModel(self.play2table)

        self.body.addWidget(self.playtable)
        self.setLayout(self.body)


    def load_directory(self, song_dir):
        home = pathlib.Path(song_dir)
        files = (element for element in home.iterdir() if element.is_file() and element.name.endswith(".ogg"))
        for fake_id, file in enumerate(files):
            media = CustomContent(QtCore.QUrl(str(file)), fake_id)
            self.playlist.addMedia(media)






def main(song_dir):
    app = QtWidgets.QApplication(sys.argv)
    view = BasicPlayer()
    view.load_directory(song_dir)
    view.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("song_dir")
    args = parser.parse_args()

    main(args.song_dir)