"""

    Resources:
        https://doc.qt.io/qtforpython/PySide6/QtCore/QAbstractItemModel.html
        https://doc.qt.io/qtforpython/PySide6/QtCore/QAbstractTableModel.html
        https://doc.qt.io/qtforpython/PySide6/QtWidgets/QMainWindow.html

    Goal:
        Experiment with composite view

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

    # def flags(self, index):
    #     return [Qt.ItemIsSelectable]



class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
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
        self.model1 = BasicModel(data)
        self.model2 = BasicModel(data)
        self.model3 = BasicModel(data)

        # our widgets
        self.table1 = QtWidgets.QTableView()
        self.table2 = QtWidgets.QTableView()
        divide = QtWidgets.QSplitter()
        self.table3 = QtWidgets.QTableView()

        # get rid of the vertical headers
        for table in [self.table1, self.table2, self.table3]:
            table.verticalHeader().hide()
            table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)


        # setup the data
        self.table1.setModel(self.model1)
        self.table2.setModel(self.model2)
        self.table3.setModel(self.model3)

        # layouts
        # top body
        self.top = QtWidgets.QHBoxLayout()
        self.top.setAlignment(Qt.AlignLeft)
        self.top.addWidget(self.table1, True, Qt.AlignLeft)
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


def main(argv):
    app = QtWidgets.QApplication(argv)
    window = MainWindow()
    window.show()
    app.exec_()



if __name__ == "__main__":
    main(sys.argv)