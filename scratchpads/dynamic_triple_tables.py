"""

    Resources:
        https://doc.qt.io/qtforpython/PySide6/QtCore/QAbstractItemModel.html
        https://doc.qt.io/qtforpython/PySide6/QtCore/QAbstractTableModel.html
        https://doc.qt.io/qtforpython/PySide6/QtWidgets/QMainWindow.html

    Goal:
        Experiment with composite view

"""

import sys
import sqlite3

import PySide2
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import Qt

class DynamicModel(QtCore.QAbstractTableModel):

    def __init__(self, header_map, initial_data):
        super(DynamicModel, self).__init__()
        self._header_map = header_map
        self._headers = list(header_map.keys())
        self._data = initial_data

    def headerData(self, section:int, orientation:PySide2.QtCore.Qt.Orientation, role:int=...):

        if role == Qt.DisplayRole:
            try:
                return self._headers[section]
            except IndexError:
                print(f"hD - index{section=}")


    def data(self, index, role):
        if role in [Qt.DisplayRole, Qt.ToolTipRole]:
            row = self._data[index.row()]
            column_name = list(self._header_map.values())[index.column()]
            return row[column_name]
        else:
            pass

        return

    def fetch_row(self, row):
        return self._data[row]

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, parent:PySide2.QtCore.QModelIndex=...) -> int:
        return len(self._header_map)

    def sort(self, column:int, order:PySide2.QtCore.Qt.SortOrder=...) -> None:

        if column == -1:
            return


        # self.emit(PySide2.QtCore.SIGNAL("layoutAboutToBeChanged()") )
        self.layoutAboutToBeChanged.emit()
        column_name = list(self._header_map.values())[column]

        if order == PySide2.QtCore.Qt.SortOrder.DescendingOrder:
            self._data = sorted(self._data, key=lambda row: row[column_name])
        else:
            self._data.sort(key=lambda row: row[column_name], reverse=True)
        self.layoutChanged.emit()
        # self.emit(PySide2.QtCore.SIGNAL("layoutChanged()"))

    def updateData(self, data):

        self.layoutAboutToBeChanged.emit()
        self._data = data
        self.layoutChanged.emit()


class TripleApp(PySide2.QtCore.QObject):

    def __init__(self, parent, default_db = "pysongman.sqlite3"):
        super().__init__(parent)

        self.conn = sqlite3.connect(default_db)
        self.conn.row_factory = sqlite3.Row

        self.artist_model = None
        self.album_model = None
        self.song_model = None


    def build_artist_model(self):
        data = []
        header_map = {
                         "artist": "name",
                         "Album Counts": "album_count",
                         "Track count": "track_count"
        }

        cursor = self.conn.cursor()

        cursor.execute("SELECT * FROM Artist")
        artists = cursor.fetchall()

        for artist in artists:
            cursor.execute("SELECT count() as 'count' FROM ArtistAlbum where artist_id = ?", [artist['id']])
            album_count = cursor.fetchone()['count']

            cursor.execute("SELECT count() as 'count' FROM Song WHERE artist_id = ?", [artist['id']])
            song_count = cursor.fetchone()['count']

            data.append(
                {
                    "id": artist['id'],
                    "name": artist['name'],
                    "album_count": album_count,
                    "track_count": song_count
                })

        model = DynamicModel(header_map, data)
        self.artist_model = model
        return model


    def build_album_model(self):
        data = []
        header_map = {
                "Album name":"name",
                "Track count": "count"
        }

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM ArtistAlbum")
        albums = cursor.fetchall()
        for album in albums:
            cursor.execute("SELECT count() as 'count' FROM Song WHERE album_id=?", [album['id']])
            count = cursor.fetchone()['count']
            row = {"id": album['id'], 'name': album['name'], 'count': count}
            data.append(row)

        cursor.close()
        model = DynamicModel(header_map, data)
        self.album_model = model
        return self.album_model

    def build_songs_model(self):
        data = []
        header_map = {
            'Artist': 'artist_name',
            "Title": "title",
            "Album": "album",
            "Track": "track",
            "Length": 'duration',
        }

        cursor = self.conn.cursor()
        cursor.execute("""
                SELECT 
                    song.id as id, 
                    song.title as title, 
                    song.track as track, 
                    song.duration as duration, 
                    ArtistAlbum.name as album_name,
                    Artist.name as artist_name
                FROM
                    Song
                LEFT JOIN
                    Artist, ArtistAlbum
                WHERE
                    Song.artist_id = Artist.id AND Song.album_id = ArtistAlbum.id
            """)

        rows = cursor.fetchall()

        for row in rows:
            data.append(dict(
                id=row['id'],
                artist_name=row['artist_name'],
                title=row['title'],
                album=row['album_name'],
                track=row['track'],
                duration=row['duration'],
            ))

        self.song_model = DynamicModel(header_map, data)
        return self.song_model




    def artist_row_clicked(self, index: PySide2.QtCore.QModelIndex):
        data = []
        record = index.model().fetch_row(index.row())
        cursor = self.conn.cursor()

        cursor.execute("SELECT * FROM ArtistAlbum where artist_id = ?", [record['id']])
        albums = cursor.fetchall()

        for album in albums:
            cursor.execute("SELECT count() as 'count' FROM Song WHERE album_id=?",[album['id']])
            count = cursor.fetchone()['count']
            data.append({'id': album['id'], 'name': album['name'], 'count': count})

        self.album_model.updateData(data)
        #fuck me I need to access the TableView from here to deselect the rows.


    def album_row_clicked(self, index: PySide2.QtCore.QModelIndex):
        data = []



class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, controller: TripleApp):
        super().__init__()

        # our data
        self.artist_model = controller.build_artist_model()
        self.album_model = controller.build_album_model()
        self.song_model = controller.build_songs_model()

        # our widgets
        self.artist_table = QtWidgets.QTableView()
        self.album_table = QtWidgets.QTableView()
        divide = QtWidgets.QSplitter()
        self.songs_table = QtWidgets.QTableView()

        # get rid of the vertical headers
        for table in [self.artist_table, self.album_table, self.songs_table]:
            table.verticalHeader().hide()
            table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            table.setSortingEnabled(True)
            table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        # setup the data
        self.artist_table.setModel(self.artist_model)
        self.album_table.setModel(self.album_model)
        self.songs_table.setModel(self.song_model)

        # layouts
        # top body
        self.top = QtWidgets.QHBoxLayout()
        self.top.setAlignment(Qt.AlignLeft)
        self.top.addWidget(self.artist_table, 1, Qt.AlignLeft)
        self.top.addWidget(self.album_table, 1, Qt.AlignLeft)

        # main body
        self.body = QtWidgets.QVBoxLayout()
        self.body.addLayout(self.top)
        self.body.setAlignment(Qt.AlignLeft)  # Ever get a feeling I really want this to be alligned left?
        self.body.addWidget(divide)
        self.body.addWidget(self.songs_table)


        self.frame = QtWidgets.QFrame(self)
        self.frame.setLayout(self.body)

        self.setCentralWidget(self.frame)

        self.setWindowTitle("Media Library")

    def bindApp(self, app):

        self.artist_table.clicked.connect(app.artist_row_clicked)
        self.album_table.clicked.connect(app.album_row_clicked)
        pass



def main(argv):
    app = QtWidgets.QApplication(argv)
    table_controller = TripleApp(app)
    window = MainWindow(table_controller)


    window.bindApp(table_controller)

    window.show()
    app.exec_()



if __name__ == "__main__":
    main(sys.argv)