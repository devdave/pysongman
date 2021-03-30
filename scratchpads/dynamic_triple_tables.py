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


class BasicModel(QtCore.QAbstractTableModel):

    def __init__(self, data):
        super(BasicModel, self).__init__()  # TODO research why the author used super this way
        self._data = data


    def headerData(self, section, orientation, role):

        if role == Qt.DisplayRole:
            return f"Test {section}"

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]

        elif role == Qt.ToolTipRole:
            return f"This is a tool tip for [{index.row()}][{index.column()}]"

        else:
            pass

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0])

    # def flags(self, index):
    #     return [Qt.ItemIsSelectable]


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

        # I know I am ding this wrong as this is really tedious
        self.emit(PySide2.QtCore.SIGNAL("layoutAboutToBeChanged()") )
        column_name = list(self._header_map.values())[column]

        if order == PySide2.QtCore.Qt.SortOrder.DescendingOrder:
            self._data = sorted(self._data, key=lambda row: row[column_name])
        else:
            self._data.sort(key=lambda row: row[column_name], reverse=True)

        self.emit(PySide2.QtCore.SIGNAL("layoutChanged()"))

    def updateData(self, data):

        self.layoutAboutToBeChanged.emit()
        # self.emit(PySide2.QtCore.SIGNAL("layoutAboutToBeChanged()"))
        self._data = data
        self.layoutChanged.emit()
        # self.emit(PySide2.QtCore.SIGNAL("layoutChanged()"))


class TripleApp(PySide2.QtCore.QObject):

    def __init__(self, parent, default_db = "pysongman.sqlite3"):
        super().__init__(parent)

        self.conn = sqlite3.connect(default_db)
        self.conn.row_factory = sqlite3.Row


    def build_artist_model(self):
        data = []
        header_map = {
                         "artist": "Artists",
                         "Album Counts": "album_count",
                         "Track count": "track_counts"
        }

        cursor = self.conn.cursor()

        cursor.execute("SELECT * FROM Artist")
        artists = cursor.fetchall()

        for artist in artists:
            cursor.execute("SELECT count() as 'count' FROM ArtistAlbum where artist_id = ?", [artist['id']])
            album_count = cursor.fetchone()['count']

            cursor.execute("SELECT count() as 'count' FROM Song WHERE artist_id = ?", [artist['id']])
            song_count = cursor.fetchone()['count']

            data.append({"name": artist['name'], "album_count": album_count, "track_count": song_count})

        return DynamicModel(header_map, data)




    def artist_row_clicked(self, index: PySide2.QtCore.QModelIndex):
        print(index.row(), index.column(), index.model().fetch_row(index.row()) )




class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, controller: TripleApp):
        super().__init__()

        # copy & pasted
        data = [
            [4, 9, 2],
            [1, 0, 0],
            [3, 5, 0],
            [3, 3, 2],
            [7, 8, 9],
        ]

        # our data
        self.model1 = controller.build_artist_model()
        self.model2 = BasicModel(data)
        self.model3 = BasicModel(data)

        # our widgets
        self.artist_table = QtWidgets.QTableView()
        self.table2 = QtWidgets.QTableView()
        divide = QtWidgets.QSplitter()
        self.table3 = QtWidgets.QTableView()

        # get rid of the vertical headers
        for table in [self.artist_table, self.table2, self.table3]:
            table.verticalHeader().hide()
            table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)


        # setup the data
        self.artist_table.setModel(self.model1)
        self.table2.setModel(self.model2)
        self.table3.setModel(self.model3)

        # layouts
        # top body
        self.top = QtWidgets.QHBoxLayout()
        self.top.setAlignment(Qt.AlignLeft)
        self.top.addWidget(self.artist_table, True, Qt.AlignLeft)
        self.top.addWidget(self.table2, True, Qt.AlignLeft)

        # main body
        self.body = QtWidgets.QVBoxLayout()
        self.body.addLayout(self.top)
        self.body.setAlignment(Qt.AlignLeft)  # Ever get a feeling I really want this to be alligned left?
        self.body.addWidget(divide)
        self.body.addWidget(self.table3)


        self.frame = QtWidgets.QFrame(self)
        self.frame.setLayout(self.body)

        self.setCentralWidget(self.frame)

        self.setWindowTitle("Triple View")

    def bindApp(self, app):


        self.artist_table.clicked.connect(app.artist_row_clicked)
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