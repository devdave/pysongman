"""

    Resources:
        https://www.learnpyqt.com/tutorials/qtableview-modelviews-numpy-pandas/
        https://doc.qt.io/qtforpython/PySide6/QtCore/QAbstractTableModel.html?highlight=qabstracttablemodel#PySide6.QtCore.PySide6.QtCore.QAbstractTableModel

    Goal:
        Touch-type copy code example and run.

"""

import sys
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import Qt


class BasicModel(QtCore.QAbstractTableModel):

    def __init__(self, data):
        super(BasicModel, self).__init__()  # TODO research why the author used super this way
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0])


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.table = QtWidgets.QTableView()

        # copy & pasted
        data = [
            [4, 9, 2],
            [1, 0, 0],
            [3, 5, 0],
            [3, 3, 2],
            [7, 8, 9],
        ]




def main():
    pass


if __name__ == "__main__":
    main()