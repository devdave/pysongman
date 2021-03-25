import sys

from PySide2 import QtWidgets
from PySide2.QtQuick import QQuickView
from PySide2.QtCore import Qt
from PySide2 import QtCore

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


def main(argv):
    data = [
        [4, 9, 2],
        [1, 0, 0],
        [3, 5, 0],
        [3, 3, 2],
        [7, 8, 9],
    ]

    myModel = BasicModel(data)


    app = QtWidgets.QApplication(argv)
    view = QQuickView()
    view.rootContext().setContextProperty("myModel", myModel)
    url = QtCore.QUrl("table.qml")
    view.setSource(url)

    # TODO somehow connect myModel python to QML Table view.

    view.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main(sys.argv)