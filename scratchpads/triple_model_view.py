"""

    Resources:
        https://doc.qt.io/qtforpython/PySide6/QtCore/QAbstractItemModel.html
        https://doc.qt.io/qtforpython/PySide6/QtCore/QAbstractTableModel.html

    Goal:
        Experiment with AbstractModel virtual functions

"""

import sys
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

        self.model = BasicModel(data)
        self.table.setModel(self.model)


        self.setWindowTitle("Triple View")
        self.setCentralWidget(self.table)





def main(argv):
    app = QtWidgets.QApplication(argv)
    window = MainWindow()
    window.show()
    app.exec_()



if __name__ == "__main__":
    main(sys.argv)