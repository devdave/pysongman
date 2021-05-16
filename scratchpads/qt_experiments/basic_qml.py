import sys
from PySide2 import QtWidgets
from PySide2.QtQuick import QQuickView
from PySide2 import QtCore




def main(argv):
    app = QtWidgets.QApplication(argv)
    view = QQuickView()
    url = QtCore.QUrl("basic.qml")

    view.setSource(url)
    view.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main(sys.argv)